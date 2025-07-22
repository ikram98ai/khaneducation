from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
import logging
from ..models import Lesson, PracticeTask, Quiz
from .. import schemas, database

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


@router.get("/{lesson_id}/quizzes/", response_model=List[schemas.Quiz])
def get_quizzes(
    lesson_id: int,
    db: Session = Depends(database.get_db),
):
    try:
        quizzes = db.query(Quiz).filter(Quiz.lesson_id == lesson_id).all()
        # if not quizzes:
        #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No lesson found for this subject")
        return [schemas.Quiz.model_validate(quiz) for quiz in quizzes]
    except SQLAlchemyError as e:
        logger.error(f"Error fetching quizzes for lesson {lesson_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
