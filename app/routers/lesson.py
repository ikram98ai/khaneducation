from fastapi import APIRouter, Depends, HTTPException, status,Response
from typing import List, Optional
import logging
from .. import crud, schemas, models, services
from ..dependencies import get_current_student

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/lessons", tags=["lessons"])

@router.get("/{lesson_id}/", response_model=schemas.Lesson)
def get_lesson(lesson_id: str):
    try:
        lesson = crud.crud_lesson.get(hash_key=lesson_id)
        if not lesson:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No lesson found for this subject")
        return lesson
    except Exception as e:
        logger.error(f"Error fetching lesson {lesson_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")



@router.get("/{lesson_id}/tasks/", response_model=List[schemas.PracticeTask])
def get_tasks(lesson_id: str):
    try:
        tasks = crud.crud_practice_task.get_by_lesson(lesson_id=lesson_id)
        return tasks
    except Exception as e:
        logger.error(f"Error fetching tasks for lesson {lesson_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")


@router.get("/{lesson_id}/quiz/", response_model=Optional[schemas.Quiz])
def get_quiz(lesson_id: str, student: models.Student = Depends(get_current_student)):
    try:
        quizzes = crud.crud_quiz.get_by_lesson_student(lesson_id=lesson_id, student_id=student.user_id)
        # Check for successful quiz attempts for this lesson by the student
        if any(quiz.passed for quiz in quizzes):
            return Response("The Quiz is completed")
      
        if len(quizzes) < 3:
            return services.generate_quiz(lesson_id, student.user_id)


  
    except Exception as e:
        logger.error(f"Error fetching quiz for lesson {lesson_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )


@router.get("/{lesson_id}/attempts/", response_model=List[schemas.QuizAttempt])
def get_quiz_attempts(lesson_id: str, student: models.Student = Depends(get_current_student)):
    try:
        quizzes = crud.crud_quiz.get_by_lesson_student(lesson_id=lesson_id, student_id=student.user_id)
        attempts = []
        for quiz in quizzes:
            attempts.append(schemas.QuizAttempt.model_validate(quiz))
        return attempts
    except Exception as e:
        logger.error(f"Error fetching quiz attempts for lesson {lesson_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )