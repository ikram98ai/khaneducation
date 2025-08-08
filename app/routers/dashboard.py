from fastapi import APIRouter, Depends, HTTPException, status
from .. import schemas, services, models, crud
from ..dependencies import get_current_student
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

def get_student_practice_tasks(student_id: str):
    try:
        student = crud.crud_student.get_by_user_id(student_id)
        enrolled_subject_ids = [e.subject_id for e in student.get_active_enrollments()]
        if not enrolled_subject_ids:
            return []
        
        all_tasks = []
        for subject_id in enrolled_subject_ids:
            lessons = crud.crud_lesson.get_by_subject_and_language(subject_id=subject_id,language=student.language)
            for lesson in lessons:
                tasks = crud.crud_practice_task.get_by_lesson(lesson_id=lesson.id)
                all_tasks.extend(tasks)
        return all_tasks[:10]
    except models.Student.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    except Exception as e:
        logger.error(f"Error fetching practice tasks for student {student_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")


@router.get("/student/", response_model=schemas.StudentDashboard)
def student_dashboard(
    current_student: models.Student = Depends(get_current_student),
):
    try:
        enrollments_data = []
        for enrollment in current_student.get_active_enrollments():
            try:
                subject = crud.crud_subject.get(hash_key=enrollment.subject_id)
                if not subject:
                    logger.warning(f"Subject with id {enrollment.subject_id} not found for student {current_student.user_id}")
                    continue

                lessons = crud.crud_lesson.get_by_subject_and_language(subject_id=subject.id, language=current_student.language)
                total_lessons = len(lessons)
                
                completed_lessons = 0
                for lesson in lessons:
                    quizzes = crud.crud_quiz.get_by_lesson(lesson_id=lesson.id)
                    for quiz in quizzes:
                        passed_attempts = crud.crud_quiz_attempt.get_by_student_and_quiz(student_id=current_student.user_id, quiz_id=quiz.id)
                        if any(attempt.passed for attempt in passed_attempts):
                            completed_lessons += 1
                            break # Move to the next lesson once a passed attempt is found
                
                progress = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
                
                enrollments_data.append(
                    schemas.EnrolledSubject(
                        id=subject.id,
                        name=subject.name,
                        description=subject.description,
                        grade_level=subject.grade_level,
                        enrolled_at=enrollment.enrolled_at,
                        total_lessons=total_lessons,
                        completed_lessons=completed_lessons,
                        progress=progress,
                    )
                )
            except models.Subject.DoesNotExist:
                logger.warning(f"Subject with id {enrollment.subject_id} not found for student {current_student.user_id}")

        recent_attempts = crud.crud_quiz_attempt.get_by_student(student_id=current_student.user_id)

        return {
            "enrollments": enrollments_data,
            "recent_attempts": recent_attempts[:5],
        }
    except Exception as e:
        logger.error(f"Error fetching student dashboard for student {current_student.user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

@router.get("/student/stats/", response_model=schemas.DashboardStats)
def student_stats(
    current_student: models.Student = Depends(get_current_student),
):
    try:
        return services.get_student_dashboard_stats(current_student.user_id)
    except Exception as e:
        logger.error(f"Error fetching student stats for student {current_student.user_id}: {e}")
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