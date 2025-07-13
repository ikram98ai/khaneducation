from sqlalchemy.orm import Session
from . import models, schemas
from typing import Type, TypeVar, Generic, List, Optional
from .database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=schemas.BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=schemas.BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        obj_data = obj_in.dict(exclude_unset=True)
        for key, value in obj_data.items():
            setattr(db_obj, key, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj


class CRUDSubject(CRUDBase[models.Subject, schemas.SubjectCreate, schemas.SubjectCreate]):
    pass


class CRUDLesson(CRUDBase[models.Lesson, schemas.LessonCreate, schemas.LessonCreate]):
    pass


class CRUDStudent(CRUDBase[models.Student, schemas.StudentCreate, schemas.StudentCreate]):
    pass


class CRUDEnrollment(CRUDBase[models.Enrollment, schemas.EnrollmentBase, schemas.EnrollmentBase]):
    pass


class CRUDPracticeTask(CRUDBase[models.PracticeTask, schemas.PracticeTaskBase, schemas.PracticeTaskBase]):
    pass


class CRUDQuiz(CRUDBase[models.Quiz, schemas.QuizBase, schemas.QuizBase]):
    pass


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


crud_subject = CRUDSubject(models.Subject)
crud_lesson = CRUDLesson(models.Lesson)
crud_student = CRUDStudent(models.Student)
crud_enrollment = CRUDEnrollment(models.Enrollment)
crud_practice_task = CRUDPracticeTask(models.PracticeTask)
crud_quiz = CRUDQuiz(models.Quiz)
crud_quiz_attempt = CRUDQuizAttempt(models.QuizAttempt)
crud_student_response = CRUDStudentResponse(models.StudentResponse)
