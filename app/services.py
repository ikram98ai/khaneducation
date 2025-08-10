# app/services.py
from typing import List
from fastapi import BackgroundTasks
from . import schemas
from .ai import generate_content as ai
from .models import Lesson, PracticeTask, Quiz, QuizAttempt, Student, Subject
from pynamodb.transactions import TransactWrite
from pynamodb.exceptions import TransactWriteError
from pynamodb.connection import Connection
from datetime import datetime, timezone
import uuid
from .utils import run_in_thread, chunked
import asyncio
from . import crud
from collections import defaultdict


async def get_subject_details_data(subject: Subject, student: Student) -> schemas.SubjectDetail:
    # 0. get lessons (assume this is already a query on subject+language)
    lessons = await run_in_thread(crud.crud_lesson.get_by_subject_and_language, subject.id, student.language)
    if not lessons:
        return schemas.SubjectDetail(
            id=subject.id, name=subject.name, description=subject.description,
            grade_level=subject.grade_level, total_lessons=0, completed_lessons=0,
            progress=0.0, lessons=[]
        )

    lesson_ids = [lesson.id for lesson in lessons]
    lesson_id_set = set(lesson_ids)

    # 1. get student's attempts (query the GSI 'by_student_id' — only that student's attempts)
    # Project only fields we need
    attr_select = ['quiz_id', 'passed', 'end_time', 'score', 'lesson_id']  # include lesson_id if denormalized
    all_attempts = await run_in_thread(
        lambda: crud.crud_quiz_attempt.get_by_student(student.user_id,extra=False,attributes_to_get=attr_select)
    )

    # 2. filter passed attempts for quizzes that belong to this subject (two approaches)
    passed_attempts = [a for a in all_attempts if getattr(a, 'passed', False)]

    # If attempts have lesson_id stored, we can directly compute completed lessons
    if passed_attempts and hasattr(passed_attempts[0], 'lesson_id') and passed_attempts[0].lesson_id:
        completed_lesson_ids = {a.lesson_id for a in passed_attempts if a.lesson_id in lesson_id_set}
    else:
        # Need to map quiz_id -> lesson_id. Collect unique quiz ids and batch_get quizzes
        passed_quiz_ids = {a.quiz_id for a in passed_attempts if getattr(a, 'quiz_id', None)}
        completed_lesson_ids = set()
        if passed_quiz_ids:
            # batch_get in chunks to respect DynamoDB limits
            for chunk in chunked(passed_quiz_ids):
                quizzes = await run_in_thread(lambda: list(Quiz.batch_get(chunk, attributes_to_get=['id', 'lesson_id'])))
                completed_lesson_ids.update(q.lesson_id for q in quizzes if q.lesson_id in lesson_id_set)

    # 3. Build lessons_with_progress
    lessons_with_progress = []
    completed_set = completed_lesson_ids
    for lesson in lessons:
        lesson_schema = schemas.Lesson.model_validate(lesson)
        lesson_schema.progress = 100.0 if lesson.id in completed_set else 0.0
        lessons_with_progress.append(lesson_schema)

    total_lessons = len(lessons)
    completed_count = len(completed_set)
    progress = (completed_count / total_lessons) * 100 if total_lessons else 0.0

    return schemas.SubjectDetail(
        id=subject.id, name=subject.name, description=subject.description,
        grade_level=subject.grade_level, total_lessons=total_lessons,
        completed_lessons=completed_count, progress=progress,
        lessons=lessons_with_progress
    )


async def get_student_dashboard_data(student: Student) -> tuple[List[schemas.EnrolledSubject], schemas.DashboardStats]:
    active_enrollments = student.get_active_enrollments()
    enrolled_subject_ids = [e.subject_id for e in active_enrollments]
    if not enrolled_subject_ids:
        return [], schemas.DashboardStats(completed_lessons=0, total_lessons=0, avg_score=0, streak=0)

    # 1. Batch get subjects (chunk if needed)
    subjects = []
    for chunk in chunked(enrolled_subject_ids):
        subjects.extend(await run_in_thread(lambda: list(Subject.batch_get(chunk, attributes_to_get=['id','name','description','grade_level']))))
    subject_map = {s.id: s for s in subjects}

    # 2. Query lessons for each subject concurrently (assumes lesson.query or crud.get_by_subject is query)
    async def fetch_lessons_for_subject(subject_id):
        return await run_in_thread(lambda: crud.crud_lesson.get_by_subject_and_language(subject_id,student.language, attributes_to_get=['id','subject_id']))
    tasks = [fetch_lessons_for_subject(sid) for sid in enrolled_subject_ids]
    results = await asyncio.gather(*tasks)
    all_lessons = [lesson for res in results for lesson in res]

    # Map lessons by subject
    lessons_by_subject = defaultdict(list)
    for lesson in all_lessons:
        lessons_by_subject[lesson.subject_id].append(lesson)

    # 3. Get all attempts for student (query GSI)
    attr_select = ['quiz_id', 'passed', 'end_time', 'score', 'lesson_id']
    all_attempts = await run_in_thread(
        lambda: crud.crud_quiz_attempt.get_by_student(student.user_id,extra=False,attributes_to_get=attr_select)
)
    passed_attempts = [a for a in all_attempts if getattr(a, 'passed', False)]

    # 4. Determine completed lesson ids
    if passed_attempts and hasattr(passed_attempts[0], 'lesson_id') and passed_attempts[0].lesson_id:
        completed_lesson_ids = {a.lesson_id for a in passed_attempts}
    else:
        passed_quiz_ids = {a.quiz_id for a in passed_attempts if getattr(a, 'quiz_id', None)}
        completed_lesson_ids = set()
        for chunk in chunked(passed_quiz_ids):
            quizzes = await run_in_thread(lambda: list(Quiz.batch_get(chunk, attributes_to_get=['id','lesson_id'])))
            completed_lesson_ids.update(q.lesson_id for q in quizzes)

    # 5. Build enrollments_data
    enrollments_data = []
    for enrollment in active_enrollments:
        subject = subject_map.get(enrollment.subject_id)
        if not subject:
            continue
        subject_lessons = lessons_by_subject.get(subject.id, [])
        total = len(subject_lessons)
        completed = sum(1 for l in subject_lessons if l.id in completed_lesson_ids)
        progress = (completed / total) * 100 if total else 0.0

        enrollments_data.append(
            schemas.EnrolledSubject(
                id=subject.id,
                name=subject.name,
                description=subject.description,
                grade_level=subject.grade_level,
                enrolled_at=enrollment.enrolled_at,
                total_lessons=total,
                completed_lessons=completed,
                progress=progress
            )
        )

    # 6. Dashboard stats
    completed_lessons_total = len(completed_lesson_ids)
    total_lessons = len(all_lessons)

    scored_attempts = [a for a in all_attempts if getattr(a, 'score', None) is not None]
    avg_score = (sum(a.score for a in scored_attempts) / len(scored_attempts)) if scored_attempts else 0.0

    # Streak calculation — sort passed attempts by end_time and compute longest consecutive-day streak
    streak = 0
    if passed_attempts:
        # extract unique dates of passed attempts
        dates = sorted({a.end_time.date() for a in passed_attempts})
        if dates:
            longest = 1
            current = 1
            for i in range(1, len(dates)):
                if (dates[i] - dates[i-1]).days == 1:
                    current += 1
                else:
                    longest = max(longest, current)
                    current = 1
            longest = max(longest, current)
            streak = longest

    stats = schemas.DashboardStats(
        completed_lessons=completed_lessons_total,
        total_lessons=total_lessons,
        avg_score=avg_score,
        streak=streak
    )
    return enrollments_data, stats


async def create_lesson_content(lesson_id: str, subject: str, grade_level: int, language_value: str, title: str):
    try:
        lesson_content = await ai.generate_lesson(
            subject=subject,
            title=title,
            grade_level=grade_level,
            language=language_value,
        )

        db_lesson = crud.crud_lesson.get(hash_key=lesson_id)
        if not db_lesson:
            print(f"Lesson with id {lesson_id} not found.")
            return

        db_lesson.content = lesson_content
        db_lesson.status = "draft"
        
        practice_tasks = await ai.generate_practice_tasks(
            lesson_content=lesson_content,
            grade_level=grade_level,
            language=language_value,
        )
        tasks = []
        for task in practice_tasks:
            new_task_id = str(uuid.uuid4())
            task_obj = PracticeTask(
                id=new_task_id,
                lesson_id=lesson_id,
                lesson_title=title,
                content=task.content,
                solution=task.solution,
                difficulty=task.difficulty,
                ai_generated=True,
                created_at=datetime.now(timezone.utc)
            )
            tasks.append(task_obj)

        new_quiz_id = str(uuid.uuid4())
        db_quiz = Quiz(
            id=new_quiz_id,
            lesson_id=lesson_id,
            lesson_title=title,
            quiz_version=1,
            ai_generated=True,
            created_at=datetime.now(timezone.utc)
        )

        quiz_questions = await ai.generate_quiz_questions(
            lesson_content=lesson_content,
            grade_level=grade_level,
            language=language_value,
        )

        for question_data in quiz_questions:
            db_quiz.add_question(
                question_text=question_data.question_text,
                question_type=question_data.question_type,
                options=question_data.options,
                correct_answer=question_data.correct_answer,
            )

        conn = Connection(region='us-east-1')
        with TransactWrite(connection=conn) as transaction:
            transaction.save(db_lesson)
            transaction.save(db_quiz)
            for task in tasks:
                transaction.save(task)

    except TransactWriteError as e:
        print(f"Transaction failed: {e}")
        # Handle transaction error, maybe update lesson status to 'FAILED'
        db_lesson.status = "failed"
        db_lesson.save()
    except Exception as e:
        print(f"Error in create_lesson_content: {e}")
        db_lesson.status = "failed"
        db_lesson.save()


async def create_lesson(
    subject_id: str,
    subject: str,
    grade_level: int,
    language_value: str,
    instructor_id: str,
    title: str,
    background_tasks: BackgroundTasks
) -> Lesson:
    new_lesson_id = str(uuid.uuid4())
    db_lesson = Lesson(
        subject_id=subject_id,
        id=new_lesson_id,
        instructor_id=instructor_id,
        title=title,
        language= language_value,
        content="Pending",
        status="pending",
        created_at=datetime.now(timezone.utc),
    )
    db_lesson.save()

    background_tasks.add_task(
        create_lesson_content,
        lesson_id=new_lesson_id,
        subject=subject,
        grade_level=grade_level,
        language_value=language_value,
        title=title
    )

    return db_lesson

MAX_QUIZ_ATTEMPTS = 3
async def submit_quiz_responses(quiz_id: str, student_id: str, responses: List[schemas.QuizResponse]) -> schemas.QuizSubmissionResponse:
    try:
        try:
            quiz = Quiz.get(quiz_id)
        except Quiz.DoesNotExist:
            raise ValueError("Quiz not found")

        # Create quiz attempt
        previous_attempts = crud.crud_quiz_attempt.get_by_student_and_quiz(student_id, quiz_id)
        attempt_number = len(previous_attempts) + 1

        if attempt_number > MAX_QUIZ_ATTEMPTS:
            raise ValueError("Exceeded maximum number of attempts")

        new_attempt_id = str(uuid.uuid4())
        db_attempt = QuizAttempt(
            student_id=student_id,  # hash key
            id=new_attempt_id,  # range key
            quiz_id=quiz_id,  # Link to quiz
            attempt_number=attempt_number,
            start_time=datetime.now(timezone.utc),
            # end_time, score, passed will be set later
            passed=False,
            cheating_detected=False,
        )
        db_attempt.finish_attempt()
        db_attempt.save()  # Save initial attempt

        student_answers = []
        correct_answers = []

        # Process responses
        for response in responses:
            question_id = response.question_id
            answer = response.student_answer
            # Fetch question
            question = next((q for q in quiz.quiz_questions if q.question_id == question_id), None)
            
            if not question:
                # Or handle this case more gracefully
                raise ValueError(f"Question with id {question_id} not found in quiz {quiz_id}")

            is_correct = answer.strip().lower() == question.correct_answer.strip().lower()
            student_answers.append(answer)
            correct_answers.append(question.correct_answer)
            db_attempt.add_response(
                question_id=question_id,  # Link to question
                student_answer=answer,
                is_correct=is_correct,
            )

        # Generate AI feedback
        ai_feedback = await ai.generate_quiz_feedback(student_answers=student_answers, correct_answers=correct_answers)
        
        db_attempt.ai_feedback = ai_feedback
        db_attempt.calculate_score()
        db_attempt.save()  # Update the attempt record

        # Regenerate quiz if needed
        regenerated_quiz = None
        if (not db_attempt.passed) and quiz.ai_generated:
            try:
                lesson = Lesson.get(quiz.lesson_id) if quiz.lesson_id else None
                if lesson:
                    student = crud.crud_student.get_by_user_id(student_id) 
                    if student:
                        quizzes_for_lesson = list(Quiz.lesson_index.query(lesson.id))
                        max_version = max((q.quiz_version for q in quizzes_for_lesson))
                        print("Max version found:", max_version)
                        new_version = max_version + 1
                        new_quiz_questions = ai.generate_quiz_questions(
                            lesson_content=lesson.content,
                            grade_level=student.current_grade,
                            language=student.language,
                        )
                        # Create new quiz
                        new_quiz_id_2 = str(uuid.uuid4())
                        new_quiz = Quiz(id=new_quiz_id_2, lesson_id=lesson.id, lesson_title= lesson.title,quiz_version=new_version, ai_generated=True, created_at=datetime.now(timezone.utc))
                        
                        # Create new questions
                        for question_data in new_quiz_questions:
                            new_quiz.add_question(
                                    question_text=question_data["question_text"],
                                    question_type=question_data["question_type"],
                                    options=question_data["options"],
                                    correct_answer=question_data["correct_answer"],
                                )
                        new_quiz.save()
                        regenerated_quiz = new_quiz

            except Lesson.DoesNotExist:
                print("Lesson not found for quiz during regeneration")
                regenerated_quiz = None
            except Student.DoesNotExist:
                print(f"Student with id {student_id} not found")
                regenerated_quiz = None
            except Exception as e:
                print(f"Error during quiz regeneration: {e}")
                regenerated_quiz = None

        lesson = Lesson.get(quiz.lesson_id) if quiz.lesson_id else None
        attempt_schema_data = schemas.QuizAttempt(
            id=db_attempt.id,
            quiz_id=db_attempt.quiz_id,
            student_id=db_attempt.student_id,
            start_time=db_attempt.start_time,
            end_time=db_attempt.end_time,
            ai_feedback=db_attempt.ai_feedback,
            score=db_attempt.score,
            passed=db_attempt.passed,
            quiz_version=quiz.quiz_version,
            cheating_detected=db_attempt.cheating_detected,
            lesson_title=lesson.title if lesson else ""
        )

        regenerated_quiz_schema = None
        if regenerated_quiz:
            # Convert PynamoDB quiz_questions to Pydantic models
            quiz_questions_schema = [
                schemas.QuizQuestion(
                    question_id=q.question_id,
                    question_text=q.question_text,
                    question_type=q.question_type,
                    options=q.options,
                    correct_answer=q.correct_answer,
                )
                for q in regenerated_quiz.quiz_questions
            ]

            regenerated_quiz_schema = schemas.Quiz(
                id=regenerated_quiz.id,
                lesson_id=regenerated_quiz.lesson_id,
                quiz_version=regenerated_quiz.quiz_version,
                ai_generated=regenerated_quiz.ai_generated,
                created_at=regenerated_quiz.created_at,
                lesson_title=regenerated_quiz.lesson_title,
                quiz_questions=quiz_questions_schema,
            )
        return schemas.QuizSubmissionResponse(
            attempt=attempt_schema_data,
            ai_feedback=ai_feedback,
            regenerated_quiz=regenerated_quiz_schema,
        )

    except Exception as e:
        print(f"Error in submit_quiz_responses: {e}")
        raise



