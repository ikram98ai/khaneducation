from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud, database
from typing import List

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.post("/", response_model=schemas.Subject)
def create_subject(subject: schemas.SubjectCreate, db: Session = Depends(database.get_db)):
    return crud.crud_subject.create(db, obj_in=subject)


@router.get("/", response_model=List[schemas.Subject])
def read_subjects(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return crud.crud_subject.get_multi(db, skip=skip, limit=limit)


@router.get("/{subject_id}", response_model=schemas.Subject)
def read_subject(subject_id: int, db: Session = Depends(database.get_db)):
    subject = crud.crud_subject.get(db, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject
