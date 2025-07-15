from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas
from ..database import get_db
from ..dependencies import get_current_admin

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_admin)],
    responses={404: {"description": "Not found"}},
)


# User routes
@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user_by_email = crud.crud_user.get_by_email(db, email=user.email)
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user_by_username = crud.crud_user.get_by_username(db, username=user.username)
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    return crud.crud_user.create(db=db, obj_in=user)


@router.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.crud_user.get_multi(db, skip=skip, limit=limit)
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found")
    return users


@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.crud_user.get(db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.crud_user.get(db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.crud_user.update(db=db, db_obj=db_user, obj_in=user)


@router.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.crud_user.get(db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.crud_user.remove(db=db, id=user_id)


# Subject routes
@router.post("/subjects/", response_model=schemas.Subject)
def create_subject(subject: schemas.SubjectCreate, db: Session = Depends(get_db)):
    return crud.crud_subject.create(db=db, obj_in=subject)


@router.get("/subjects/", response_model=List[schemas.Subject])
def read_subjects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    subjects = crud.crud_subject.get_multi(db, skip=skip, limit=limit)
    if not subjects:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No subjects found")
    return subjects


@router.put("/subjects/{subject_id}", response_model=schemas.Subject)
def update_subject(subject_id: int, subject: schemas.SubjectCreate, db: Session = Depends(get_db)):
    db_subject = crud.crud_subject.get(db, id=subject_id)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return crud.crud_subject.update(db=db, db_obj=db_subject, obj_in=subject)


@router.delete("/subjects/{subject_id}", response_model=schemas.Subject)
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    db_subject = crud.crud_subject.get(db, id=subject_id)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return crud.crud_subject.remove(db=db, id=subject_id)


# Nested Lesson routes
@router.post("/subjects/{subject_id}/lessons/", response_model=schemas.Lesson)
async def create_lesson_for_subject(
    subject_id: int, lesson: schemas.LessonCreate, db: Session = Depends(get_db), current_admin: schemas.User = Depends(get_current_admin)
):
    db_subject = crud.crud_subject.get(db, id=subject_id)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    lesson.subject_id = subject_id
    lesson.instructor_id = current_admin.id
    db_lesson = crud.crud_lesson.create(db=db, obj_in=lesson)
    return schemas.Lesson.from_orm(db_lesson)


@router.get("/subjects/{subject_id}/lessons/", response_model=List[schemas.Lesson])
def read_lessons_for_subject(subject_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_subject = crud.crud_subject.get(db, id=subject_id)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    lessons = crud.crud_lesson.get_multi_by_subject(db, subject_id=subject_id, skip=skip, limit=limit)
    # if not lessons:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No lessons found for this subject")
    return [schemas.Lesson.from_orm(lesson) for lesson in lessons]


# Individual Lesson routes
@router.get("/lessons/{lesson_id}", response_model=schemas.Lesson)
def read_lesson(lesson_id: int, db: Session = Depends(get_db)):
    db_lesson = crud.crud_lesson.get(db, id=lesson_id)
    if db_lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return schemas.Lesson.from_orm(db_lesson)


@router.put("/lessons/{lesson_id}", response_model=schemas.Lesson)
def update_lesson(lesson_id: int, lesson: schemas.LessonCreate, db: Session = Depends(get_db)):
    print("DEBUG:: PUT lesson:: ",lesson)
    db_lesson = crud.crud_lesson.get(db, id=lesson_id)
    if db_lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    db_lesson = crud.crud_lesson.update(db=db, db_obj=db_lesson, obj_in=lesson)
    return schemas.Lesson.from_orm(db_lesson)


@router.delete("/lessons/{lesson_id}", response_model=schemas.Lesson)
def delete_lesson(lesson_id: int, db: Session = Depends(get_db)):
    db_lesson = crud.crud_lesson.get(db, id=lesson_id)
    if db_lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    db_lesson = crud.crud_lesson.remove(db=db, id=lesson_id)
    return schemas.Lesson.from_orm(db_lesson)


# Nested PracticeTask routes
@router.post("/lessons/{lesson_id}/practice_tasks/", response_model=schemas.PracticeTask)
def create_task_for_lesson(lesson_id: int, task: schemas.PracticeTaskBase, db: Session = Depends(get_db)):
    db_lesson = crud.crud_lesson.get(db, id=lesson_id)
    if db_lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    db_task = crud.crud_practice_task.create(db=db, obj_in=task)
    return schemas.PracticeTask.from_orm(db_task)


@router.get("/lessons/{lesson_id}/practice_tasks/", response_model=List[schemas.PracticeTask])
def read_tasks_for_lesson(lesson_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_lesson = crud.crud_lesson.get(db, id=lesson_id)
    if db_lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    tasks = crud.crud_practice_task.get_multi_by_lesson(db, lesson_id=lesson_id, skip=skip, limit=limit)
    if not tasks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No tasks found for this lesson")
    return [schemas.PracticeTask.from_orm(task) for task in tasks]


# Nested Quiz routes
@router.post("/lessons/{lesson_id}/quizzes/", response_model=schemas.Quiz)
def create_quiz_for_lesson(lesson_id: int, quiz: schemas.QuizBase, db: Session = Depends(get_db)):
    db_lesson = crud.crud_lesson.get(db, id=lesson_id)
    if db_lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    quiz.lesson_id = lesson_id
    db_quiz = crud.crud_quiz.create(db=db, obj_in=quiz)
    return schemas.Quiz.from_orm(db_quiz)


@router.get("/lessons/{lesson_id}/quizzes/", response_model=List[schemas.Quiz])
def read_quizzes_for_lesson(lesson_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_lesson = crud.crud_lesson.get(db, id=lesson_id)
    if db_lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    quizzes = crud.crud_quiz.get_multi_by_lesson(db, lesson_id=lesson_id, skip=skip, limit=limit)
    if not quizzes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No quizzes found for this lesson")
    return [schemas.Quiz.from_orm(quiz) for quiz in quizzes]
