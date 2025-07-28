from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from . import models, schemas, crud
from .ai import generate_content as ai
from datetime import datetime, timedelta
from typing import List, Dict, Any


def create_lesson_with_content(db: Session, subject_id: int, instructor_id: int, title: str) -> models.Lesson:
    try:
        subject = crud.crud_subject.get(db, subject_id)
        if not subject:
            raise ValueError("Subject not found")

        lesson_content = ai.generate_lesson(
            title=title,
            grade_level=subject.grade_level,
            language=subject.language.value,
        )

        lesson_in = schemas.LessonCreate(subject_id=subject_id, instructor_id=instructor_id, title=title, content=lesson_content)

        db_lesson = crud.crud_lesson.create(db, obj_in=lesson_in, commit=False)
        db.flush()
        db_lesson.status = models.LessonStatus.DRAFT

        # Create practice task
        task_content = ai.generate_practice_task(
            lesson_content=lesson_content,
            difficulty="ME",
            grade_level=subject.grade_level,
            language=subject.language.value,
        )
        crud.crud_practice_task.create(
            db,
            obj_in=schemas.PracticeTaskBase(lesson_id=db_lesson.id, content=task_content, difficulty="ME"),
            commit=False
        )

        # Create quiz
        quiz_data = ai.generate_quiz(
            lesson_content=lesson_content,
            grade_level=subject.grade_level,
            language=subject.language.value,
        )
        db_quiz = crud.crud_quiz.create(db, obj_in=schemas.QuizBase(lesson_id=db_lesson.id, version=1), commit=False)
        db.flush()

        for question in quiz_data["questions"]:
            crud.crud_quiz_question.create(
                db,
                obj_in=schemas.QuizQuestionBase(
                    quiz_id=db_quiz.id,
                    question_text=question["question"],
                    option_a=question["option_a"],
                    option_b=question["option_b"],
                    option_c=question["option_c"],
                    option_d=question["option_d"],
                    correct_answer=question["correct_answer"],
                ),
                commit=False
            )

        db.commit()
        db.refresh(db_lesson)
        return db_lesson
    except Exception:
        db.rollback()
        raise


def submit_quiz_responses(db: Session, quiz_id: int, student_id: int, responses: List[schemas.QuizResponse]) -> schemas.QuizSubmissionResponse:
    try:
        quiz = crud.crud_quiz.get(db, quiz_id)
        if not quiz:
            raise ValueError("Quiz not found")

        # Create quiz attempt
        attempt_in = schemas.QuizAttemptBase(quiz_id=quiz_id, student_id=student_id)
        db_attempt = crud.crud_quiz_attempt.create(db, obj_in=attempt_in, commit=False)
        db.flush()

        correct_count = 0
        student_answers = []
        correct_answers = []

        # Process responses
        for response in responses:
            question_id = response.question_id
            answer = response.answer

            question = crud.crud_quiz_question.get(db, question_id)
            if not question:
                continue

            is_correct = answer.strip().lower() == question.correct_answer.strip().lower()
            if is_correct:
                correct_count += 1

            student_answers.append(answer)
            correct_answers.append(question.correct_answer)

            # Create response record
            crud.crud_student_response.create(
                db,
                obj_in=schemas.StudentResponseBase(
                    attempt_id=db_attempt.id,
                    question_id=question_id,
                    student_answer=answer,
                    is_correct=is_correct,
                ),
                commit=False
            )

        # Calculate score
        total_questions = len(responses)
        score = (correct_count / total_questions) * 100 if total_questions > 0 else 0

        # Update attempt
        db_attempt.score = score
        db_attempt.passed = score >= 70
        db_attempt.end_time = datetime.utcnow()

        # Generate AI feedback
        ai_feedback = ai.generate_quiz_feedback(student_answers=student_answers, correct_answers=correct_answers)

        # Regenerate quiz if needed
        regenerated_quiz = None
        if score < 60 and quiz.ai_generated:
            lesson = quiz.lesson
            new_version = max([q.version for q in lesson.quizzes] or [0]) + 1

            new_quiz_data = ai.generate_quiz(
                lesson_content=lesson.content,
                grade_level=lesson.subject.grade_level,
                language=lesson.subject.language.value,
            )

            new_quiz = crud.crud_quiz.create(
                db,
                obj_in=schemas.QuizBase(lesson_id=lesson.id, version=new_version),
                commit=False
            )
            db.flush()

            for question in new_quiz_data["questions"]:
                crud.crud_quiz_question.create(
                    db,
                    obj_in=schemas.QuizQuestionBase(
                        quiz_id=new_quiz.id,
                        question_text=question["question"],
                        option_a=question["option_a"],
                        option_b=question["option_b"],
                        option_c=question["option_c"],
                        option_d=question["option_d"],
                        correct_answer=question["correct_answer"],
                    ),
                    commit=False
                )
            regenerated_quiz = new_quiz

        db.commit()

        db.refresh(db_attempt)
        if regenerated_quiz:
            db.refresh(regenerated_quiz)

        return {
            "attempt": db_attempt,
            "ai_feedback": ai_feedback,
            "regenerated_quiz": regenerated_quiz,
        }
    except Exception:
        db.rollback()
        raise


def get_student_dashboard_stats(db: Session, student_id: int) -> schemas.DashboardStats:
    # Completed lessons
    completed_lessons = (
        db.query(models.Lesson)
        .join(models.Quiz)
        .join(models.QuizAttempt)
        .filter(
            models.QuizAttempt.student_id == student_id,
            models.QuizAttempt.passed,
        )
        .distinct()
        .count()
    )

    # Total lessons
    enrolled_subjects = db.query(models.Enrollment.subject_id).filter(models.Enrollment.student_id == student_id).subquery()

    total_lessons = db.query(models.Lesson).filter(models.Lesson.subject_id.in_(enrolled_subjects.select())).count()

    # Average score
    avg_score = db.query(func.avg(models.QuizAttempt.score)).filter(models.QuizAttempt.student_id == student_id).scalar() or 0

    # Streak calculation
    today = datetime.utcnow().date()
    streak = 0
    current_date = today

    while True:
        has_attempt = (
            db.query(models.QuizAttempt)
            .filter(
                models.QuizAttempt.student_id == student_id,
                func.date(models.QuizAttempt.end_time) == current_date,
                models.QuizAttempt.passed,
            )
            .first()
        )

        if not has_attempt:
            break

        streak += 1
        current_date -= timedelta(days=1)

    return {
        "completedLessons": completed_lessons,
        "totalLessons": total_lessons,
        "avgScore": round(avg_score, 2),
        "streak": streak,
    }
