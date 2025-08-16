# app/services.py
from typing import List, Dict, Tuple
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

def group_attempts_by_lesson(attempts: List[Quiz]) -> Dict[str, List[Quiz]]:
    lesson_attempts = defaultdict(list)
    for a in attempts:
        lesson_attempts[a.lesson_id].append(a)
    return lesson_attempts

def analyze_attempts(attempts: List[Quiz]) -> Tuple[int, bool]:
    """Return (max_score, is_completed) for a lesson's attempts"""
    max_score, is_completed = 0, False
    for a in attempts:
        if a.score > max_score:
            max_score = a.score
        if a.passed:
            is_completed = True
    return max_score, is_completed

def calculate_streak(passed_attempts: List[Quiz]) -> int:
    """Longest streak of consecutive days with a passed attempt"""
    dates = sorted({a.end_time.date() for a in passed_attempts if a.end_time})
    if not dates:
        return 0
    longest = current = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days == 1:
            current += 1
        else:
            longest = max(longest, current)
            current = 1
    return max(longest, current)


async def get_subject_details_data(subject: Subject, student: Student) -> schemas.SubjectDetail:
    # 0. get lessons (assume this is already a query on subject+language)
    lessons, attempted_quizzes = await asyncio.gather(
        run_in_thread(crud.crud_lesson.get_by_subject_and_language, subject.id, student.language),
        run_in_thread(crud.crud_quiz.get_by_subject_student, subject.id, student.user_id)
    )    
    if not lessons:
        return schemas.SubjectDetail(
            id=subject.id,
            name=subject.name,
            description=subject.description,
            grade_level=subject.grade_level
        )

    lesson_attempts = group_attempts_by_lesson(attempted_quizzes)

    completed_count = 0    
    # 3. Build lessons_with_progress
    lessons_with_progress = []
    for lesson in lessons:
        attempts = lesson_attempts[lesson.id]
        max_score, is_completed = analyze_attempts(attempts)            
        lesson_schema = schemas.SubjectLesson.model_validate(lesson)
        lesson_schema.progress = max_score
        lesson_schema.quiz_attempts = len(attempts)
        lesson_schema.is_completed = is_completed
        lessons_with_progress.append(lesson_schema)
        if is_completed:
            completed_count+=1

    total_lessons = len(lessons)
    progress = (completed_count / total_lessons) * 100 if total_lessons else 0.0

    return schemas.SubjectDetail(
        id=subject.id,
        name=subject.name,
        description=subject.description,
        grade_level=subject.grade_level,
        total_lessons=total_lessons,
        completed_lessons=completed_count,
        progress=progress,
        lessons= lessons_with_progress 
    )


async def get_student_dashboard_data(student: Student) -> schemas.StudentDashboard:
    enrolled_subjects = await run_in_thread(crud.crud_subject.get_by_grade, student.current_grade)
    if not enrolled_subjects:
        return schemas.StudentDashboard(enrollments=[], stats=schemas.DashboardStats(completed_lessons=0, total_lessons=0, avg_score=0, streak=0))

    # 2. Query lessons for each subject concurrently (assumes lesson.query or crud.get_by_subject is query)
    async def fetch_subject(subject):
        return await get_subject_details_data(subject, student)

    tasks = [fetch_subject(subject) for subject in enrolled_subjects]
    results = await asyncio.gather(*tasks)
    subjects: List[schemas.SubjectDetail] = [subject for subject in results]
    # 5. Build enrollments_data
    enrollments_data = []
    total_completed_lessons = 0
    total_lessons = 0
    for subject in subjects:
        total_completed_lessons += subject.completed_lessons
        total_lessons += subject.total_lessons
        enrollments_data.append(
            schemas.Subject.model_validate(subject)
        )

    # 6. Dashboard stats
    all_attempts = await run_in_thread(crud.crud_quiz.get_by_student,student.user_id)
    
    passed_attempts = []
    total_score = 0
    scored_count = 0
    for a in all_attempts:
        if getattr(a, "score", None) is not None:
            total_score += a.score
            scored_count += 1
        if getattr(a, "passed", False):
            passed_attempts.append(a)

    avg_score = (total_score / scored_count) if scored_count else 0.0
    streak = calculate_streak(passed_attempts)

    stats = schemas.DashboardStats(completed_lessons=total_completed_lessons, total_lessons=total_lessons, avg_score=avg_score, streak=streak)
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
                created_at=datetime.now(timezone.utc),
            )
            tasks.append(task_obj)

        conn = Connection(region="us-east-1")
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
    subject_id: str, subject: str, grade_level: int, language_value: str, instructor_id: str, title: str, background_tasks: BackgroundTasks
) -> Lesson:
    new_lesson_id = str(uuid.uuid4())
    db_lesson = Lesson(
        subject_id=subject_id,
        id=new_lesson_id,
        instructor_id=instructor_id,
        title=title,
        language=language_value,
        content="Pending",
        status="pending",
        created_at=datetime.now(timezone.utc),
    )
    db_lesson.save()

    background_tasks.add_task(
        create_lesson_content, lesson_id=new_lesson_id, subject=subject, grade_level=grade_level, language_value=language_value, title=title
    )

    return db_lesson


async def generate_quiz(lesson: Lesson, student: Student) -> schemas.Quiz:
    try:
        try:
            quizzes = crud.crud_quiz.get_by_lesson_student(lesson.id, student.user_id)
            quiz_version = max([quiz.quiz_version for quiz in quizzes]) + 1
        except Exception as e:
            print("Exception in generating quiz: ", str(e))
            quiz_version = 1

        if quiz_version >= 3:
            raise ValueError(
                f"Student: {student.user_id}, is not able create a new quiz for lesson {lesson.id} due to limited quiz attemtps (3 attempts only)."
            )

        db_quiz = Quiz(
            lesson_id=lesson.id,
            student_id=student.user_id,
            subject_id=lesson.subject_id,
            lesson_title=lesson.title,
            quiz_version=quiz_version,
            start_time=datetime.now(timezone.utc),
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
