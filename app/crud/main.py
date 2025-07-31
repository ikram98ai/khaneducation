# app/crud/main.py
from ..models import (
    User,
    Subject,
    Lesson,
    Student,
    PracticeTask,
    Quiz,
    QuizAttempt,
    StudentProgress,
    Notification,
    LessonRating,
    StudySession
)
from .base import CRUDBase
from typing import List, Optional
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class CRUDUser(CRUDBase[User]):
    def get_by_email(self, email: str) -> Optional[User]:
        try:
            results = list(self.model.email_index.query(email))
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Error fetching user by email {email}: {e}")
            raise HTTPException(status_code=500, detail="Database error")

    def get_by_username(self, username: str) -> Optional[User]:
        try:
            results = list(self.model.username_index.query(username))
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Error fetching user by username {username}: {e}")
            raise HTTPException(status_code=500, detail="Database error")

class CRUDSubject(CRUDBase[Subject]):
    def get_by_grade_and_language(self, grade_level: int, language: str) -> List[Subject]:
        try:
            return list(self.model.grade_level_index.query(grade_level, Subject.language == language))
        except Exception as e:
            logger.error(f"Error fetching subjects by grade and language: {e}")
            raise HTTPException(status_code=500, detail="Database error")

class CRUDLesson(CRUDBase[Lesson]):
    def get_by_subject(self, subject_id: str) -> List[Lesson]:
        try:
            return list(self.model.subject_index.query(subject_id))
        except Exception as e:
            logger.error(f"Error fetching lessons for subject {subject_id}: {e}")
            raise HTTPException(status_code=500, detail="Database error")

    def get_by_instructor(self, instructor_id: str) -> List[Lesson]:
        try:
            return list(self.model.instructor_index.query(instructor_id))
        except Exception as e:
            logger.error(f"Error fetching lessons for instructor {instructor_id}: {e}")
            raise HTTPException(status_code=500, detail="Database error")

class CRUDStudent(CRUDBase[Student]):
    def get_by_user_id(self, user_id: str) -> Optional[Student]:
        try:
            # This assumes you have a GSI on user_id or you are using a scan.
            # For a scalable solution, a GSI on user_id is recommended.
            results = list(self.model.scan(Student.user_id == user_id))
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Error fetching student by user_id {user_id}: {e}")
            raise HTTPException(status_code=500, detail="Database error")

class CRUDQuizAttempt(CRUDBase[QuizAttempt]):
    def get_by_student(self, student_id: str) -> List[QuizAttempt]:
        try:
            return list(self.model.student_index.query(student_id))
        except Exception as e:
            logger.error(f"Error fetching quiz attempts for student {student_id}: {e}")
            raise HTTPException(status_code=500, detail="Database error")

class CRUDStudentProgress(CRUDBase[StudentProgress]):
    def get_by_student_and_lesson(self, student_id: str, lesson_id: str) -> Optional[StudentProgress]:
        try:
            # This assumes a GSI is not strictly necessary if get_multi is not frequently used for this model.
            # A scan is used here, but for performance, consider a GSI on (student_id, lesson_id).
            results = list(self.model.scan((StudentProgress.student_id == student_id) & (StudentProgress.lesson_id == lesson_id)))
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Error fetching student progress for student {student_id} and lesson {lesson_id}: {e}")
            raise HTTPException(status_code=500, detail="Database error")

# Instantiate CRUD objects
crud_user = CRUDUser(User)
crud_subject = CRUDSubject(Subject)
crud_lesson = CRUDLesson(Lesson)
crud_student = CRUDStudent(Student)
crud_practice_task = CRUDBase(PracticeTask)
crud_quiz = CRUDBase(Quiz)
crud_quiz_attempt = CRUDQuizAttempt(QuizAttempt)
crud_student_progress = CRUDStudentProgress(StudentProgress)
crud_notification = CRUDBase(Notification)
crud_lesson_rating = CRUDBase(LessonRating)
crud_study_session = CRUDBase(StudySession)