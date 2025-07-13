from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud, database, models, services
from typing import List, Optional
from ..dependencies import get_current_student

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
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/attempts", response_model=List[schemas.QuizAttempt])
def get_quiz_attempts(
    student_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
):
    query = db.query(models.QuizAttempt)
    if student_id:
        query = query.filter(models.QuizAttempt.student_id == student_id)
    return query.offset(skip).limit(limit).all()


@router.get("/attempts/{attempt_id}", response_model=schemas.QuizAttempt)
def get_quiz_attempt(attempt_id: int, db: Session = Depends(database.get_db)):
    attempt = crud.crud_quiz_attempt.get(db, attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    return attempt
