# app/crud/main_pynamodb.py (or replace app/crud/main.py)
# from .. import models, schemas # Remove SQLAlchemy models
# from .base import CRUDBase # Remove old base
# from typing import List, Optional # Keep if needed
# from sqlalchemy.orm import Session # Remove
# --- PynamoDB Imports ---
from ..models import Subject, Lesson, Student, Enrollment, PracticeTask, Quiz, QuizQuestion, QuizAttempt, StudentResponse, User # Import PynamoDB models
from .base import CRUDBase # Import new PynamoDB base
from typing import List, Optional
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

# --- Specific CRUD Classes for PynamoDB Models ---

class CRUDSubject(CRUDBase[Subject]):
    def get_multi(self, skip: int = 0, limit: int = 100) -> List[Subject]:
        # Example using scan (inefficient for large datasets)
        # Consider pagination or specific query patterns
        try:
            all_items = list(self.model.scan())
            return all_items[skip : skip + limit]
        except Exception as e:
            logger.error(f"Error fetching subjects: {e}")
            raise HTTPException(status_code=500, detail="Database error")

class CRUDLesson(CRUDBase[Lesson]):
    def get_multi_by_subject(self, subject_id: int, skip: int = 0, limit: int = 100) -> List[Lesson]:
        # Requires GSI or appropriate key structure (e.g., subject_id as hash key)
        # Example if Lesson has subject_id as hash key:
        try:
            lessons = list(self.model.query(subject_id)) # Query by hash key
            return lessons[skip : skip + limit]
        except Exception as e:
            logger.error(f"Error fetching lessons for subject {subject_id}: {e}")
            raise HTTPException(status_code=500, detail="Database error")

class CRUDStudent(CRUDBase[Student]):
    pass # Add specific methods if needed

class CRUDEnrollment(CRUDBase[Enrollment]):
    pass # Add specific methods if needed

class CRUDPracticeTask(CRUDBase[PracticeTask]):
    def get_multi_by_lesson(self, lesson_id: int, skip: int = 0, limit: int = 100) -> List[PracticeTask]:
        # Requires GSI or appropriate key structure (e.g., lesson_id as hash key)
         try:
            tasks = list(self.model.query(lesson_id)) # Example query
            return tasks[skip : skip + limit]
         except Exception as e:
            logger.error(f"Error fetching tasks for lesson {lesson_id}: {e}")
            raise HTTPException(status_code=500, detail="Database error")

class CRUDQuiz(CRUDBase[Quiz]):
    def get_multi_by_lesson(self, lesson_id: int, skip: int = 0, limit: int = 100) -> List[Quiz]:
        # Requires GSI or appropriate key structure
         try:
            quizzes = list(self.model.query(lesson_id)) # Example query
            return quizzes[skip : skip + limit]
         except Exception as e:
            logger.error(f"Error fetching quizzes for lesson {lesson_id}: {e}")
            raise HTTPException(status_code=500, detail="Database error")

class CrudQuizQuestion(CRUDBase[QuizQuestion]):
    pass

class CRUDQuizAttempt(CRUDBase[QuizAttempt]):
    pass

class CRUDStudentResponse(CRUDBase[StudentResponse]):
    pass

class CRUDUser(CRUDBase[User]):
    def get_by_email(self, email: str) -> Optional[User]:
        # Requires GSI on email
        try:
            # Assuming UserEmailIndex is defined in User model
            results = list(self.model.email_index.query(email))
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Error fetching user by email {email}: {e}")
            raise HTTPException(status_code=500, detail="Database error")

    def get_by_username(self, username: str) -> Optional[User]:
        # Requires GSI on username
        try:
             # Assuming UsernameIndex is defined in User model
            results = list(self.model.username_index.query(username))
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Error fetching user by username {username}: {e}")
            raise HTTPException(status_code=500, detail="Database error")

# --- Instantiate CRUD objects for PynamoDB models ---
crud_subject = CRUDSubject(Subject)
crud_lesson = CRUDLesson(Lesson)
crud_student = CRUDStudent(Student)
crud_enrollment = CRUDEnrollment(Enrollment)
crud_practice_task = CRUDPracticeTask(PracticeTask)
crud_quiz = CRUDQuiz(Quiz)
crud_quiz_question = CrudQuizQuestion(QuizQuestion)
crud_quiz_attempt = CRUDQuizAttempt(QuizAttempt)
crud_student_response = CRUDStudentResponse(StudentResponse)
crud_user = CRUDUser(User)
