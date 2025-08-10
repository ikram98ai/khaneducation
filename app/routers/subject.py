from fastapi import APIRouter, Depends, HTTPException, status
from .. import schemas, models, crud, services
from ..dependencies import get_current_student
from typing import List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.get("/", response_model=List[schemas.Subject])
def get_subjects(limit: int = 100):
    try:
        subjects = crud.crud_subject.get_multi(limit=limit)
        if not subjects:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No subjects found")
        return subjects
    except Exception as e:
        logger.error(f"Error fetching subjects: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")


@router.get("/{subject_id}/", response_model=schemas.SubjectDetail)
def get_subject(subject_id: str):
    subject = crud.crud_subject.get(hash_key=subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    return schemas.SubjectDetail(
        id=subject.id,
        name=subject.name,
        description=subject.description,
        grade_level=subject.grade_level,
    )


@router.get("/{subject_id}/details/", response_model=schemas.SubjectDetail)
async def get_subject_details(subject_id: str, current_student: models.Student = Depends(get_current_student)):
    subject = crud.crud_subject.get(hash_key=subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    return await services.get_subject_details_data(subject, current_student)



