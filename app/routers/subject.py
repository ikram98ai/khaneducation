from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .. import schemas, crud, database
from typing import List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.post("/", response_model=schemas.Subject)
def create_subject(subject: schemas.SubjectCreate, db: Session = Depends(database.get_db)):
    try:
        return crud.crud_subject.create(db, obj_in=subject)
    except SQLAlchemyError as e:
        logger.error(f"Error creating subject: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")


@router.get("/", response_model=List[schemas.Subject])
def read_subjects(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    try:
        subjects = crud.crud_subject.get_multi(db, skip=skip, limit=limit)
        if not subjects:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No subjects found")
        return subjects
    except SQLAlchemyError as e:
        logger.error(f"Error fetching subjects: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")


@router.get("/{subject_id}", response_model=schemas.Subject)
def read_subject(subject_id: int, db: Session = Depends(database.get_db)):
    subject = crud.crud_subject.get(db, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject
