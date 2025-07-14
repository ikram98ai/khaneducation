from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import schemas, database, services, models
from ..dependencies import get_current_student

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def get_student_practice_tasks(db: Session, student_id: int):
    enrolled_subjects = db.query(models.Enrollment.subject_id).filter(models.Enrollment.student_id == student_id).subquery()
    return db.query(models.PracticeTask).join(models.Lesson).filter(models.Lesson.subject_id.in_(enrolled_subjects)).limit(10).all()


@router.get("/student", response_model=schemas.StudentDashboard)
def student_dashboard(
    db: Session = Depends(database.get_db),
    current_student: models.Student = Depends(get_current_student),
):
    return {
        "student": current_student,
        "enrollments": current_student.enrollments,
        "recent_attempts": current_student.quiz_attempts[:5],
        "practice_tasks": get_student_practice_tasks(db, current_student.user_id),
    }


@router.get("/student/stats", response_model=schemas.DashboardStats)
def student_stats(
    db: Session = Depends(database.get_db),
    current_student: models.Student = Depends(get_current_student),
):
    return services.get_student_dashboard_stats(db, current_student.user_id)


@router.get("/admin", response_model=dict)
def admin_dashboard(db: Session = Depends(database.get_db)):
    return {
        "total_students": db.query(models.Student).count(),
        "total_lessons": db.query(models.Lesson).count(),
        "total_subjects": db.query(models.Subject).count(),
        "total_quizzes": db.query(models.Quiz).count(),
        "recent_lessons": db.query(models.Lesson).order_by(models.Lesson.created_at.desc()).limit(5).all(),
        "recent_attempts": db.query(models.QuizAttempt).order_by(models.QuizAttempt.start_time.desc()).limit(10).all(),
    }
