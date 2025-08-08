from fastapi import APIRouter, Depends, HTTPException, status
from .. import schemas, models, crud
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
def get_subject(subject_id: str, current_student: models.Student = Depends(get_current_student)):
    subject = crud.crud_subject.get(hash_key=subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    lessons = crud.crud_lesson.get_by_subject(subject_id=subject.id)
    total_lessons = len(lessons)

    completed_lessons_count = 0

    for lesson in lessons:
        quizzes = crud.crud_quiz.get_by_lesson(lesson_id=lesson.id)
        for quiz in quizzes:
            lesson_quiz_attempts = crud.crud_quiz_attempt.get_by_student_and_quiz(student_id=current_student.user_id, quiz_id=quiz.id)
            if any(attempt.passed for attempt in lesson_quiz_attempts):
                completed_lessons_count += 1
                break

    return schemas.SubjectDetail(
        id=subject.id,
        name=subject.name,
        description=subject.description,
        grade_level=subject.grade_level,
        total_lessons=total_lessons,
        completed_lessons=completed_lessons_count,
        progress=(completed_lessons_count / total_lessons) * 100 if total_lessons > 0 else 0,
    )


@router.get("/{subject_id}/details/", response_model=schemas.SubjectDetail)
def get_subject_details(subject_id: str, current_student: models.Student = Depends(get_current_student)):
    subject = crud.crud_subject.get(hash_key=subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    lessons = crud.crud_lesson.get_by_subject_and_language(subject_id=subject.id, language=current_student.language)
    total_lessons = len(lessons)

    completed_lessons_count = 0
    lessons_with_progress = []

    for lesson in lessons:
        quizzes = crud.crud_quiz.get_by_lesson(lesson_id=lesson.id)
        lesson_progress = 0.0
        for quiz in quizzes:
            lesson_quiz_attempts = crud.crud_quiz_attempt.get_by_student_and_quiz(student_id=current_student.user_id, quiz_id=quiz.id)
            if any(attempt.passed for attempt in lesson_quiz_attempts):
                lesson_progress = 100.0
                completed_lessons_count += 1
                break
        
        lesson.progress = lesson_progress
        lessons_with_progress.append(lesson)

    return schemas.SubjectDetail(
        id=subject.id,
        name=subject.name,
        description=subject.description,
        grade_level=subject.grade_level,
        total_lessons=total_lessons,
        completed_lessons=completed_lessons_count,
        progress=(completed_lessons_count / total_lessons) * 100 if total_lessons > 0 else 0,
        lessons=lessons_with_progress,
    )



