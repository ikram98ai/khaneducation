from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime, timezone
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
    return crud.crud_user.create(obj_in_data=user.model_dump())


@router.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100):
    users = crud.crud_user.get_multi(limit=limit)
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found")
    return users


@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: str):
    db_user = crud.crud_user.get(hash_key=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: str, user: schemas.UserCreate):
    db_user = crud.crud_user.get(hash_key=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.crud_user.update(db_obj=db_user, obj_in_data=user.model_dump())


@router.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: str):
    db_user = crud.crud_user.get(hash_key=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.crud_user.remove(db_obj=db_user)

# Subject routes
@router.post("/subjects/", response_model=schemas.Subject)
def create_subject(subject: schemas.SubjectCreate):
    new_subject = crud.crud_subject.create(obj_in_data=subject.model_dump())
    
    # Find matching students and enroll them
    students_to_enroll = crud.crud_student.get_by_grade_and_language(
        grade_level=new_subject.grade_level, 
        language=new_subject.language
    )
    
    for student in students_to_enroll:
        student.add_enrollment(subject_id=new_subject.id)
        student.save()
        
    return new_subject


@router.get("/subjects/", response_model=List[schemas.Subject])
def read_subjects(limit: int = 100):
    subjects = crud.crud_subject.get_multi(limit=limit)
    return subjects


@router.put("/subjects/{subject_id}", response_model=schemas.Subject)
def update_subject(subject_id: str, subject: schemas.SubjectCreate):
    db_subject = crud.crud_subject.get(hash_key=subject_id)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return crud.crud_subject.update(db_obj=db_subject, obj_in_data=subject.model_dump())


@router.delete("/subjects/{subject_id}", response_model=schemas.Subject)
def delete_subject(subject_id: str):
    db_subject = crud.crud_subject.get(hash_key=subject_id)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return crud.crud_subject.remove(db_obj=db_subject)


# Nested Lesson routes
@router.post("/subjects/{subject_id}/lessons/", response_model=schemas.LessonCreate)
async def create_lesson_for_subject(subject_id: str, lesson: schemas.LessonCreate, current_admin: schemas.User = Depends(get_current_admin)):
    db_subject = crud.crud_subject.get(hash_key=subject_id)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")

    lesson.subject_id = subject_id
    lesson.instructor_id = current_admin.id

    try:
        db_lesson = await services.create_lesson_with_content(subject_id, db_subject.grade_level, db_subject.language, current_admin.id, lesson.title)
        return db_lesson
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/subjects/{subject_id}/lessons/", response_model=List[schemas.Lesson])
def read_lessons_for_subject(subject_id: str, limit: int = 100):
    db_subject = crud.crud_subject.get(hash_key=subject_id)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    lessons = crud.crud_lesson.get_by_subject(subject_id=subject_id)
    return lessons


# Individual Lesson routes
@router.get("/lessons/{lesson_id}", response_model=schemas.Lesson)
def read_lesson(lesson_id: str):
    db_lesson = crud.crud_lesson.get(hash_key=lesson_id)
    if db_lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return db_lesson


@router.put("/lessons/{lesson_id}", response_model=schemas.Lesson)
def update_lesson(lesson_id: str, lesson: schemas.LessonCreate):
    db_lesson = crud.crud_lesson.get(hash_key=lesson_id)
    if db_lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return crud.crud_lesson.update(db_obj=db_lesson, obj_in_data=lesson.model_dump())


@router.delete("/lessons/{lesson_id}", response_model=schemas.Lesson)
def delete_lesson(lesson_id: str):
    db_lesson = crud.crud_lesson.get(hash_key=lesson_id)
    if db_lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return crud.crud_lesson.remove(db_obj=db_lesson)


@router.put("/lessons/{lesson_id}/verify", response_model=schemas.Lesson)
def verify_lesson(lesson_id: str):
    lesson = crud.crud_lesson.get(hash_key=lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    lesson.status = schemas.LessonStatusEnum.VERIFIED.value
    lesson.verified_at = datetime.now(timezone.utc)
    lesson.save()
    return lesson


# Nested PracticeTask routes
@router.post("/lessons/{lesson_id}/practice_tasks/", response_model=schemas.PracticeTask)
def create_task_for_lesson(lesson_id: str, task: schemas.PracticeTaskBase):
    db_lesson = crud.crud_lesson.get(hash_key=lesson_id)
    if db_lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    task_data = task.model_dump()
    task_data['lesson_id'] = lesson_id
    return crud.crud_practice_task.create(obj_in_data=task_data)


@router.get("/lessons/{lesson_id}/practice_tasks/", response_model=List[schemas.PracticeTask])
def read_tasks_for_lesson(lesson_id: str, limit: int = 100):
    db_lesson = crud.crud_lesson.get(hash_key=lesson_id)
    if db_lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    tasks = crud.crud_practice_task.get_by_lesson(lesson_id=lesson_id)
    return tasks


# Nested Quiz routes
@router.post("/lessons/{lesson_id}/quizzes/", response_model=schemas.Quiz)
def create_quiz_for_lesson(lesson_id: str, quiz: schemas.QuizBase):
    db_lesson = crud.crud_lesson.get(hash_key=lesson_id)
    if db_lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    quiz_data = quiz.model_dump()
    quiz_data['lesson_id'] = lesson_id
    return crud.crud_quiz.create(obj_in_data=quiz_data)


@router.get("/lessons/{lesson_id}/quizzes/", response_model=List[schemas.Quiz])
def read_quizzes_for_lesson(lesson_id: str, limit: int = 100):
    db_lesson = crud.crud_lesson.get(hash_key=lesson_id)
    if db_lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    quizzes = crud.crud_quiz.get_by_lesson(lesson_id=lesson_id)
    return quizzes
