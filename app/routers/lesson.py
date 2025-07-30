from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc
from typing import List, Optional
import logging
from ..models import Lesson, PracticeTask, Quiz, QuizAttempt, Student
from .. import schemas, database
from ..dependencies import get_current_student

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.get("/{lesson_id}/", response_model=schemas.Lesson)
def get_lesson(
    lesson_id: int,
    db: Session = Depends(database.get_db),
):
    try:
        lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
        if not lesson:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No lesson found for this subject")
        return schemas.Lesson.model_validate(lesson)
    except SQLAlchemyError as e:
        logger.error(f"Error fetching lesson {lesson_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")


@router.get("/{lesson_id}/tasks/", response_model=List[schemas.PracticeTask])
def get_tasks(
    lesson_id: int,
    db: Session = Depends(database.get_db),
):
    try:
        tasks = db.query(PracticeTask).filter(PracticeTask.lesson_id == lesson_id).all()
        # if not tasks:
        #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No lesson found for this subject")
        return [schemas.PracticeTask.model_validate(task) for task in tasks]
    except SQLAlchemyError as e:
        logger.error(f"Error fetching tasks for lesson {lesson_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")


@router.get("/{lesson_id}/quiz/", response_model=Optional[schemas.Quiz])
def get_quiz(
    lesson_id: int,
    db: Session = Depends(database.get_db),
    student: Student = Depends(get_current_student),
):
    try:
        # Check for successful quiz attempts for this lesson by the student
        successful_attempt = (
            db.query(QuizAttempt)
            .join(Quiz)
            .filter(
                Quiz.lesson_id == lesson_id,
                QuizAttempt.student_id == student.user_id,
                QuizAttempt.passed,
            )
            .first()
        )

        if successful_attempt:
            return None

        # If no successful attempt, load the quiz
        quiz = db.query(Quiz).filter(Quiz.lesson_id == lesson_id).order_by(desc(Quiz.version_number)).first()
        if not quiz:
            return None

        lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
        quiz_data = schemas.Quiz.model_validate(quiz).model_dump()
        quiz_data["lesson_title"] = lesson.title if lesson else None
        return schemas.Quiz.model_validate(quiz_data)
    except SQLAlchemyError as e:
        logger.error(f"Error fetching quiz for lesson {lesson_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )


@router.get("/{lesson_id}/attempts/", response_model=List[schemas.QuizAttempt])
def get_quiz_attempts(
    lesson_id: int,
    db: Session = Depends(database.get_db),
    student: Student = Depends(get_current_student),
    skip: int = 0,
    limit: int = 100,
):
    try:
        attempts = (
            db.query(QuizAttempt)
            .join(Quiz)
            .filter(Quiz.lesson_id == lesson_id, QuizAttempt.student_id == student.user_id)
            .order_by(desc(Quiz.version_number))
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [schemas.QuizAttempt.model_validate(attempt) for attempt in attempts]
    except SQLAlchemyError as e:
        logger.error(f"Error fetching quiz attempts for lesson {lesson_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )
