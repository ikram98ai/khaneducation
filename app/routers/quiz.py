from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
import logging
from ..dependencies import get_current_student
from .. import schemas, database, models, services

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


@router.post("{quiz_id}/submit", response_model=schemas.QuizSubmissionResponse)
def submit_quiz(
    quiz_id: int,
    responses: List[schemas.QuizResponse],
    db: Session = Depends(database.get_db),
    current_student: models.Student = Depends(get_current_student),
):
    try:
        return services.submit_quiz_responses(
            db,
            quiz_id,
            current_student.user_id,
            responses,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except SQLAlchemyError as e:
        logger.error(f"Error submitting quiz for student {current_student.user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
