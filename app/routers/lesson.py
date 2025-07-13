from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime
from .. import schemas, crud, database, models, services
from ..dependencies import get_current_user

router = APIRouter(prefix="/subjects/{subject_id}/lessons", tags=["lessons"])


@router.post("/", response_model=schemas.Lesson)
def create_lesson(
    subject_id: int,
    lesson: schemas.LessonCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        return services.create_lesson_with_content(db, subject_id, current_user.id, lesson.title)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[schemas.Lesson])
def read_lessons(
    subject_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
):
    return db.query(models.Lesson).filter(models.Lesson.subject_id == subject_id).offset(skip).limit(limit).all()


@router.put("/{lesson_id}/verify", response_model=schemas.Lesson)
def verify_lesson(lesson_id: int, db: Session = Depends(database.get_db)):
    lesson = crud.crud_lesson.get(db, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    lesson.status = models.LessonStatus.VERIFIED
    lesson.verified_at = datetime.utcnow()
    db.commit()
    return lesson
