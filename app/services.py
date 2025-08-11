# app/services.py
from typing import List
from fastapi import BackgroundTasks
from . import schemas
from .ai import generate_content as ai
from .models import Lesson, PracticeTask, Quiz, Student, Subject
from pynamodb.transactions import TransactWrite
from pynamodb.exceptions import TransactWriteError
from pynamodb.connection import Connection
from datetime import datetime, timezone
import uuid
from .utils import run_in_thread
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
    attr_select = ['id', 'passed', 'end_time', 'score', 'lesson_id']  # include lesson_id if denormalized
    all_attempts = await run_in_thread(
        lambda: crud.crud_quiz.get_by_student(student.user_id,attributes_to_get=attr_select)
    )

    # 2. filter passed attempts for quizzes that belong to this subject (two approaches)
    passed_attempts = [a for a in all_attempts if getattr(a, 'passed', False)]

    # If attempts have lesson_id stored, we can directly compute completed lessons
    completed_lesson_ids = {a.lesson_id for a in passed_attempts if a.lesson_id in lesson_id_set and a.passed==True}

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


async def get_student_dashboard_data(student: Student) -> schemas.StudentDashboard:
    enrolled_subjects = await run_in_thread(crud.crud_subject.get_by_grade,student.current_grade)
    enrolled_subject_ids = [s.id for s in enrolled_subjects]
    if not enrolled_subject_ids:
        return schemas.StudentDashboard(enrollments=[], stats=schemas.DashboardStats(completed_lessons=0, total_lessons=0, avg_score=0, streak=0))

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
    attr_select = ['id', 'passed', 'end_time', 'score', 'lesson_id']
    all_attempts = await run_in_thread(
        lambda: crud.crud_quiz.get_by_student(student.user_id,attributes_to_get=attr_select)
)
    passed_attempts = [a for a in all_attempts if getattr(a, 'passed', False)]

    # 4. Determine completed lesson ids
    completed_lesson_ids = {a.lesson_id for a in passed_attempts if  a.passed==True}

    # 5. Build enrollments_data
    enrollments_data = []
    for subject in enrolled_subjects:

        subject_lessons = lessons_by_subject.get(subject.id, [])
        total = len(subject_lessons)
        completed = sum(1 for l in subject_lessons if l.id in completed_lesson_ids)
        progress = (completed / total) * 100 if total else 0.0

        enrollments_data.append(
            schemas.Subject(
                id=subject.id,
                name=subject.name,
                description=subject.description,
                grade_level=subject.grade_level,
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
        dates = sorted({a.end_time.date() for a in passed_attempts if a.end_time})
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
    return schemas.StudentDashboard(enrollments=enrollments_data, stats=stats)


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


        conn = Connection(region='us-east-1')
        with TransactWrite(connection=conn) as transaction:
            transaction.save(db_lesson)
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

async def generate_quiz(lesson:Lesson, student:Student) -> schemas.Quiz:
    try:
        try:
            quizzes = crud.crud_quiz.get_by_lesson_student(lesson.id,student.user_id)
            quiz_version = max([ quiz.quiz_version for quiz in quizzes]) + 1
        except:
            quiz_version = 1 

        if quiz_version >= 3:
            raise ValueError(f"Student: {student.user_id}, is not able create a new quiz for lesson {lesson.id} due to limited quiz attemtps (3 attempts only).")


        db_quiz = Quiz(
            lesson_id=lesson.id,
            student_id=student.user_id,
            lesson_title=lesson.title,
            quiz_version=quiz_version,
            start_time=datetime.now(timezone.utc)
        )

        quiz_questions = await ai.generate_quiz_questions(
            lesson_content=lesson.content,
            grade_level=student.current_grade,
            language=lesson.language,
        )

        for question_data in quiz_questions:
            db_quiz.add_question(
                question_text=question_data.question_text,
                question_type=question_data.question_type,
                options=question_data.options,
                correct_answer=question_data.correct_answer,
            )

        db_quiz.save()
        return db_quiz
    
    except Exception as e:
        print(f"Error in generating quiz: {e}")

async def submit_quiz_responses(quiz_id: str, responses: List[schemas.QuizResponse]) -> schemas.QuizSubmissionResponse:
    try:
        try:
            quiz = Quiz.get(quiz_id)
        except Quiz.DoesNotExist:
            raise ValueError("Quiz not found")

        # Create quiz attempt
   
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
            quiz.add_response(
                question_id=question_id,  # Link to question
                student_answer=answer,
                is_correct=is_correct,
            )

        # Generate AI feedback
        ai_feedback = await ai.generate_quiz_feedback(student_answers=student_answers, correct_answers=correct_answers)
        
        quiz.ai_feedback = ai_feedback
        quiz.finish_quiz()
        quiz.save()  # Update the attempt record

        return {"attempt": quiz, "ai_feedback": ai_feedback}

    except Exception as e:
        print(f"Error in submit_quiz_responses: {e}")
        raise
