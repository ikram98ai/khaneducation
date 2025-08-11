from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
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


@router.get("/{lesson_id}/quiz/", response_model=schemas.Quiz | str)
async def get_quiz(lesson_id: str, student: models.Student = Depends(get_current_student)):
    try:
        # Check for successful quiz attempts for this lesson by the student
        lesson = crud.crud_lesson.get(lesson_id)
        new_quiz = await services.generate_quiz(lesson, student)
        return new_quiz

    except Exception as e:
        logger.error(f"Error fetching quiz for lesson {lesson_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )


@router.get("/{lesson_id}/attempts/", response_model=List[schemas.QuizAttemptOut])
def get_quiz_attempts(lesson_id: str, student: models.Student = Depends(get_current_student)):
    try:
        quizzes = crud.crud_quiz.get_by_lesson_student(lesson_id=lesson_id, student_id=student.user_id)
        attempts_out = []
        for quiz in quizzes:
            questions_map = {q.question_id: q for q in quiz.quiz_questions}

            responses_out = []
            if quiz.responses:
                for resp in quiz.responses:
                    question = questions_map.get(resp.question_id)
                    if question:
                        responses_out.append(
                            schemas.QuizAttemptResponsesOut(
                                question_id=resp.question_id,
                                question_text=question.question_text,
                                question_type=question.question_type,
                                student_answer=resp.student_answer,
                                correct_answer=question.correct_answer,
                            )
                        )

            attempts_out.append(
                schemas.QuizAttemptOut(
                    id=quiz.id,
                    lesson_title=quiz.lesson_title,
                    start_time=quiz.start_time,
                    end_time=quiz.end_time,
                    score=quiz.score,
                    passed=quiz.passed,
                    ai_feedback=quiz.ai_feedback,
                    quiz_version=quiz.quiz_version,
                    cheating_detected=quiz.cheating_detected,
                    responses=responses_out,
                )
            )
        return attempts_out
    except Exception as e:
        logger.error(f"Error fetching quiz attempts for lesson {lesson_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )
