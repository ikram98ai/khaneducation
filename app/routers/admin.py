from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
from .. import crud, schemas, models, services
from ..dependencies import get_current_admin

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_admin)],
    responses={404: {"description": "Not found"}},
)


# User routes
@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate):
    db_user_by_email = crud.crud_user.get_by_email(email=user.email)
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user_by_username = crud.crud_user.get_by_username(username=user.username)
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    return crud.crud_user.create(obj_in=user)


@router.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100):
    users = crud.crud_user.get_multi(skip=skip, limit=limit)
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found")
    return users


@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int):
    db_user = crud.crud_user.get(id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserCreate):
    db_user = crud.crud_user.get(id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.crud_user.update(db_obj=db_user, obj_in=user)


@router.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: int):
    db_user = crud.crud_user.get(id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.crud_user.remove(id=user_id)


# Subject routes
@router.post("/subjects/", response_model=schemas.Subject)
def create_subject(subject: schemas.SubjectCreate):
    try:
        new_subject = crud.crud_subject.create(obj_in=subject)

        # Find matching students and enroll them
        matching_students = (
            db.query(models.Student)
            .filter(models.Student.current_grade == new_subject.grade_level, models.Student.language == new_subject.language)
            .all()
        )

        for student in matching_students:
            enrollment = models.Enrollment(student_id=student.user_id, subject_id=new_subject.id)
            db.add(enrollment)

        if matching_students:
            db.commit()

        return new_subject
    except SQLAlchemyError:
        # logger.error(f"Error creating subject: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")


@router.get("/subjects/", response_model=List[schemas.Subject])
def read_subjects(skip: int = 0, limit: int = 100):
    subjects = crud.crud_subject.get_multi(skip=skip, limit=limit)
    # if not subjects:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No subjects found")
    return subjects


@router.put("/subjects/{subject_id}", response_model=schemas.Subject)
def update_subject(subject_id: int, subject: schemas.SubjectCreate):
    db_subject = crud.crud_subject.get(id=subject_id)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return crud.crud_subject.update(db_obj=db_subject, obj_in=subject)


@router.delete("/subjects/{subject_id}", response_model=schemas.Subject)
def delete_subject(subject_id: int):
    db_subject = crud.crud_subject.get(id=subject_id)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return crud.crud_subject.remove(id=subject_id)


# Nested Lesson routes
@router.post("/subjects/{subject_id}/lessons/", response_model=schemas.LessonCreate)
async def create_lesson_for_subject(subject_id: int, lesson: schemas.LessonCreate, current_admin: schemas.User = Depends(get_current_admin)):
    db_subject = crud.crud_subject.get(id=subject_id)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")

    lesson.subject_id = subject_id
    lesson.instructor_id = current_admin.id

    try:
        db_lesson = services.create_lesson_with_content(subject_id, current_admin.id, lesson.title)
        return schemas.Lesson.from_orm(db_lesson)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except SQLAlchemyError:
        # logger.error(f"Error creating lesson for subject {subject_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")


@router.get("/subjects/{subject_id}/lessons/", response_model=List[schemas.Lesson])
def read_lessons_for_subject(subject_id: int, skip: int = 0, limit: int = 100):
    db_subject = crud.crud_subject.get(id=subject_id)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    lessons = crud.crud_lesson.get_multi_by_subject(subject_id=subject_id, skip=skip, limit=limit)
    # if not lessons:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No lessons found for this subject")
    return [schemas.Lesson.from_orm(lesson) for lesson in lessons]


# Individual Lesson routes
@router.get("/lessons/{lesson_id}", response_model=schemas.Lesson)
def read_lesson(lesson_id: int):
    db_lesson = crud.crud_lesson.get(id=lesson_id)
    if db_lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return schemas.Lesson.from_orm(db_lesson)


@router.put("/lessons/{lesson_id}", response_model=schemas.Lesson)
def update_lesson(lesson_id: int, lesson: schemas.LessonCreate):
    print("DEBUG:: PUT lesson:: ", lesson)
    db_lesson = crud.crud_lesson.get(id=lesson_id)
    if db_lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    db_lesson = crud.crud_lesson.update(db_obj=db_lesson, obj_in=lesson)
    return schemas.Lesson.from_orm(db_lesson)


@router.delete("/lessons/{lesson_id}", response_model=schemas.Lesson)
def delete_lesson(lesson_id: int):
    db_lesson = crud.crud_lesson.get(id=lesson_id)
    if db_lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    db_lesson = crud.crud_lesson.remove(id=lesson_id)
    return schemas.Lesson.from_orm(db_lesson)


@router.put("/lessons/{lesson_id}/verify", response_model=schemas.Lesson)
def verify_lesson(lesson_id: int):
    try:
        lesson = crud.crud_lesson.get(lesson_id)
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")

        lesson.status = schemas.LessonStatusEnum.VERIFIED
        lesson.verified_at = datetime.utcnow()
        db.commit()
        return schemas.Lesson.from_orm(lesson)
    except SQLAlchemyError:
        db.rollback()
        # logger.error(f"Error verifying lesson {lesson_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")


# Nested PracticeTask routes
@router.post("/lessons/{lesson_id}/practice_tasks/", response_model=schemas.PracticeTask)
def create_task_for_lesson(lesson_id: int, task: schemas.PracticeTaskBase):
    db_lesson = crud.crud_lesson.get(id=lesson_id)
    if db_lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    db_task = crud.crud_practice_task.create(obj_in=task)
    return schemas.PracticeTask.from_orm(db_task)


@router.get("/lessons/{lesson_id}/practice_tasks/", response_model=List[schemas.PracticeTask])
def read_tasks_for_lesson(lesson_id: int, skip: int = 0, limit: int = 100):
    db_lesson = crud.crud_lesson.get(id=lesson_id)
    if db_lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    tasks = crud.crud_practice_task.get_multi_by_lesson(lesson_id=lesson_id, skip=skip, limit=limit)
    if not tasks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No tasks found for this lesson")
    return [schemas.PracticeTask.from_orm(task) for task in tasks]


# Nested Quiz routes
@router.post("/lessons/{lesson_id}/quizzes/", response_model=schemas.Quiz)
def create_quiz_for_lesson(lesson_id: int, quiz: schemas.QuizBase):
    db_lesson = crud.crud_lesson.get(id=lesson_id)
    if db_lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    quiz.lesson_id = lesson_id
    db_quiz = crud.crud_quiz.create(obj_in=quiz)
    return schemas.Quiz.from_orm(db_quiz)


@router.get("/lessons/{lesson_id}/quizzes/", response_model=List[schemas.Quiz])
def read_quizzes_for_lesson(lesson_id: int, skip: int = 0, limit: int = 100):
    db_lesson = crud.crud_lesson.get(id=lesson_id)
    if db_lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    quizzes = crud.crud_quiz.get_multi_by_lesson(lesson_id=lesson_id, skip=skip, limit=limit)
    if not quizzes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No quizzes found for this lesson")
    return [schemas.Quiz.from_orm(quiz) for quiz in quizzes]
