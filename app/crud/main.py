from .. import models, schemas
from .base import CRUDBase
from typing import List, Optional
from sqlalchemy.orm import Session


class CRUDSubject(CRUDBase[models.Subject, schemas.SubjectCreate, schemas.SubjectCreate]):
    pass


class CRUDLesson(CRUDBase[models.Lesson, schemas.LessonCreate, schemas.LessonCreate]):
    def get_multi_by_subject(self, db: Session, *, subject_id: int, skip: int = 0, limit: int = 100) -> List[models.Lesson]:
        return db.query(self.model).filter(self.model.subject_id == subject_id).offset(skip).limit(limit).all()


class CRUDStudent(CRUDBase[models.Student, schemas.StudentCreate, schemas.StudentCreate]):
    pass


class CRUDEnrollment(CRUDBase[models.Enrollment, schemas.EnrollmentBase, schemas.EnrollmentBase]):
    pass


class CRUDPracticeTask(CRUDBase[models.PracticeTask, schemas.PracticeTaskBase, schemas.PracticeTaskBase]):
    def get_multi_by_lesson(self, db: Session, *, lesson_id: int, skip: int = 0, limit: int = 100) -> List[models.PracticeTask]:
        return db.query(self.model).filter(self.model.lesson_id == lesson_id).offset(skip).limit(limit).all()


class CRUDQuiz(CRUDBase[models.Quiz, schemas.QuizBase, schemas.QuizBase]):
    def get_multi_by_lesson(self, db: Session, *, lesson_id: int, skip: int = 0, limit: int = 100) -> List[models.Quiz]:
        return db.query(self.model).filter(self.model.lesson_id == lesson_id).offset(skip).limit(limit).all()


class CRUDQuizAttempt(CRUDBase[models.QuizAttempt, schemas.QuizAttemptBase, schemas.QuizAttemptBase]):
    pass


class CRUDStudentResponse(
    CRUDBase[
        models.StudentResponse,
        schemas.StudentResponseBase,
        schemas.StudentResponseBase,
    ]
):
    pass


class CRUDUser(CRUDBase[models.User, schemas.UserCreate, schemas.UserCreate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[models.User]:
        return db.query(self.model).filter(self.model.email == email).first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[models.User]:
        return db.query(self.model).filter(self.model.username == username).first()


crud_subject = CRUDSubject(models.Subject)
crud_lesson = CRUDLesson(models.Lesson)
crud_student = CRUDStudent(models.Student)
crud_enrollment = CRUDEnrollment(models.Enrollment)
crud_practice_task = CRUDPracticeTask(models.PracticeTask)
crud_quiz = CRUDQuiz(models.Quiz)
crud_quiz_attempt = CRUDQuizAttempt(models.QuizAttempt)
crud_student_response = CRUDStudentResponse(models.StudentResponse)
crud_user = CRUDUser(models.User)
