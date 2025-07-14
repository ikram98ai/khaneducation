from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
from .. import schemas, database, services, models
from ..dependencies import get_current_student

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def get_student_practice_tasks(db: Session, student_id: int):
    try:
        enrolled_subjects = db.query(models.Enrollment.subject_id).filter(models.Enrollment.student_id == student_id).subquery()
        return db.query(models.PracticeTask).join(models.Lesson).filter(models.Lesson.subject_id.in_(enrolled_subjects)).limit(10).all()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching practice tasks for student {student_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")


@router.get("/student", response_model=schemas.StudentDashboard)
def student_dashboard(
    db: Session = Depends(database.get_db),
    current_student: models.Student = Depends(get_current_student),
):
    try:
        return {
            "student": current_student,
            "enrollments": current_student.enrollments,
            "recent_attempts": current_student.quiz_attempts[:5],
            "practice_tasks": get_student_practice_tasks(db, current_student.user_id),
        }
    except SQLAlchemyError as e:
        logger.error(f"Error fetching student dashboard for student {current_student.user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")


@router.get("/student/stats", response_model=schemas.DashboardStats)
def student_stats(
    db: Session = Depends(database.get_db),
    current_student: models.Student = Depends(get_current_student),
):
    try:
        return services.get_student_dashboard_stats(db, current_student.user_id)
    except SQLAlchemyError as e:
        logger.error(f"Error fetching student stats for student {current_student.user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")


@router.get("/admin", response_model=schemas.AdminDashboard)
def admin_dashboard(db: Session = Depends(database.get_db)):
    try:
        recent_lessons = db.query(models.Lesson).order_by(models.Lesson.created_at.desc()).limit(5).all()
        recent_attempts = db.query(models.QuizAttempt).order_by(models.QuizAttempt.start_time.desc()).limit(10).all()
        return {
            "total_students": db.query(models.Student).count(),
            "total_lessons": db.query(models.Lesson).count(),
            "total_subjects": db.query(models.Subject).count(),
            "total_quizzes": db.query(models.Quiz).count(),
            "recent_lessons": [schemas.Lesson.from_orm(lesson) for lesson in recent_lessons],
            "recent_attempts": [schemas.QuizAttempt.from_orm(attempt) for attempt in recent_attempts],
        }
    except SQLAlchemyError as e:
        logger.error(f"Error fetching admin dashboard: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
