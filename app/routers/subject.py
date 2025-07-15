from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .. import schemas, database, models
from ..crud import crud_subject
from ..dependencies import get_current_student
from typing import List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.post("/", response_model=schemas.Subject)
def create_subject(subject: schemas.SubjectCreate, db: Session = Depends(database.get_db)):
    try:
        new_subject = crud_subject.create(db, obj_in=subject)

        # Find matching students and enroll them
        matching_students = db.query(models.Student).filter(
            models.Student.current_grade == new_subject.grade_level,
            models.Student.language == new_subject.language
        ).all()

        for student in matching_students:
            enrollment = models.Enrollment(student_id=student.user_id, subject_id=new_subject.id)
            db.add(enrollment)

        if matching_students:
            db.commit()

        return new_subject
    except SQLAlchemyError as e:
        logger.error(f"Error creating subject: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")


@router.get("/", response_model=List[schemas.Subject])
def read_subjects(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    try:
        subjects = crud_subject.get_multi(db, skip=skip, limit=limit)
        if not subjects:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No subjects found")
        return subjects
    except SQLAlchemyError as e:
        logger.error(f"Error fetching subjects: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")


@router.get("/{subject_id}/", response_model=schemas.SubjectDetail)
def read_subject(subject_id: int, db: Session = Depends(database.get_db), current_student: models.Student = Depends(get_current_student)):
    subject = crud_subject.get(db, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    lessons = db.query(models.Lesson).filter(models.Lesson.subject_id == subject.id).all()
    total_lessons = len(lessons)
    
    completed_lessons_count = 0
    lessons_with_progress = []

    for lesson in lessons:
        lesson_quiz_attempts = db.query(models.QuizAttempt).join(models.Quiz).filter(
            models.Quiz.lesson_id == lesson.id,
            models.QuizAttempt.student_id == current_student.user_id,
            models.QuizAttempt.passed == True
        ).count()
        
        lesson_progress = 100.0 if lesson_quiz_attempts > 0 else 0.0
        if lesson_progress == 100.0:
            completed_lessons_count += 1

        lesson_schema = schemas.Lesson.from_orm(lesson)
        lesson_schema.progress = lesson_progress
        lessons_with_progress.append(lesson_schema)

    return schemas.SubjectDetail(id=subject.id,
                                 name=subject.name,
                                 description= subject.description,
                                 grade_level=subject.grade_level,
                                 total_lessons=total_lessons,
                                 completed_lessons = completed_lessons_count,
                                 progress = (completed_lessons_count / total_lessons) * 100 if total_lessons > 0 else 0,
                                 lessons=lessons_with_progress
                                 )
