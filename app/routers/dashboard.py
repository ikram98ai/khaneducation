from fastapi import APIRouter, Depends, HTTPException, status
from .. import schemas, services, models, crud
from ..dependencies import get_current_student
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/student/", response_model=schemas.StudentDashboard)
async def student_dashboard(
    current_student: models.Student = Depends(get_current_student),
):
    try:
        enrollments_data, stats = await services.get_student_dashboard_data(current_student)
        recent_attempts = crud.crud_quiz_attempt.get_by_student(student_id=current_student.user_id)

        return {
            "enrollments": enrollments_data,
            "recent_attempts": recent_attempts[:5],
            "stats": stats,
        }
    except Exception as e:
        logger.error(f"Error fetching student dashboard for student {current_student.user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")


@router.get("/admin/", response_model=schemas.AdminDashboard)
def admin_dashboard():
    try:
        # These will still use scan, as there's no specific index for "latest"
        # For a production system, you might implement a more sophisticated approach
        # like a dedicated "latest items" table or a more complex indexing strategy.
        recent_lessons = list(models.Lesson.scan(limit=5))
        recent_attempts = list(models.QuizAttempt.scan(limit=10))
        
        return {
            "total_students": models.Student.count(),
            "total_lessons": models.Lesson.count(),
            "total_subjects": models.Subject.count(),
            "total_quizzes": models.Quiz.count(),
            "recent_lessons": recent_lessons,
            "recent_attempts": recent_attempts,
        }
    except Exception as e:
        logger.error(f"Error fetching admin dashboard: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")