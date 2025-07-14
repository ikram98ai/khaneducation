from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .. import schemas, crud, database, models, services
from typing import List, Optional
import logging
from ..dependencies import get_current_student

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


@router.post("/submit", response_model=dict)
def submit_quiz(
    submission: schemas.QuizSubmission,
    db: Session = Depends(database.get_db),
    current_student: models.Student = Depends(get_current_student),
):
    try:
        return services.submit_quiz_responses(
            db,
            submission.quiz_id,
            current_student.user_id,
            submission.responses,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except SQLAlchemyError as e:
        logger.error(f"Error submitting quiz for student {current_student.user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")


@router.get("/attempts", response_model=List[schemas.QuizAttempt])
def get_quiz_attempts(
    student_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
):
    try:
        query = db.query(models.QuizAttempt)
        if student_id:
            query = query.filter(models.QuizAttempt.student_id == student_id)
        attempts = query.offset(skip).limit(limit).all()
        if not attempts:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No quiz attempts found")
        return [schemas.QuizAttempt.from_orm(attempt) for attempt in attempts]
    except SQLAlchemyError as e:
        logger.error(f"Error fetching quiz attempts: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")


@router.get("/attempts/{attempt_id}", response_model=schemas.QuizAttempt)
def get_quiz_attempt(attempt_id: int, db: Session = Depends(database.get_db)):
    attempt = crud.crud_quiz_attempt.get(db, attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    return schemas.QuizAttempt.from_orm(attempt)
