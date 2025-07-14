from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
import logging
from . import models, schemas
from typing import Type, TypeVar, Generic, List, Optional
from .database import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=schemas.BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=schemas.BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        try:
            return db.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching {self.model.__name__} with id {id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        try:
            return db.query(self.model).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching multiple {self.model.__name__}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        try:
            obj_in_data = obj_in.dict()
            db_obj = self.model(**obj_in_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating {self.model.__name__}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create item")

    def update(self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        try:
            obj_data = obj_in.dict(exclude_unset=True)
            for key, value in obj_data.items():
                setattr(db_obj, key, value)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error updating {self.model.__name__} with id {db_obj.id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not update item")

    def remove(self, db: Session, *, id: int) -> ModelType:
        try:
            obj = db.query(self.model).get(id)
            if not obj:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{self.model.__name__} not found")
            db.delete(obj)
            db.commit()
            return obj
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error deleting {self.model.__name__} with id {id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not delete item")


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
    pass


crud_subject = CRUDSubject(models.Subject)
crud_lesson = CRUDLesson(models.Lesson)
crud_student = CRUDStudent(models.Student)
crud_enrollment = CRUDEnrollment(models.Enrollment)
crud_practice_task = CRUDPracticeTask(models.PracticeTask)
crud_quiz = CRUDQuiz(models.Quiz)
crud_quiz_attempt = CRUDQuizAttempt(models.QuizAttempt)
crud_student_response = CRUDStudentResponse(models.StudentResponse)
crud_user = CRUDUser(models.User)
