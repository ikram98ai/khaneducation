from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .. import models, schemas, utils
from ..database import get_db
from ..dependencies import get_current_user
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(models.User).filter((models.User.email == user.email) | (models.User.username == user.username)).first()

        if existing_user:
            if existing_user.email == user.email:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered.")
            if existing_user.username == user.username:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username is already taken.")

        if not utils.is_strong_password(user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Password must be at least 8 characters long, and include at least one "
                    "uppercase letter, one lowercase letter, one digit, and one special character."
                ),
            )

        # hash the password - user.password
        hashed_password = utils.hash(user.password)
        user_data = user.model_dump()
        user_data["password"] = hashed_password

        new_user = models.User(**user_data)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create user")


@router.post("/profile/me", response_model=schemas.StudentProfile)
def create_me(profile_data: schemas.StudentCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    try:
        existing_student = db.query(models.Student).filter(models.Student.user_id == user.id).first()
        if existing_student:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student profile already exists for this user")

        new_student = models.Student(user_id=user.id, **profile_data.model_dump())
        db.add(new_student)
        db.commit()
        db.refresh(new_student)

        # Find matching subjects and enroll the student
        matching_subjects = (
            db.query(models.Subject)
            .filter(models.Subject.grade_level == new_student.current_grade, models.Subject.language == new_student.language)
            .all()
        )

        for subject in matching_subjects:
            enrollment = models.Enrollment(student_id=new_student.user_id, subject_id=subject.id)
            db.add(enrollment)

        if matching_subjects:
            db.commit()

        return schemas.StudentProfile(user=user, student_profile=new_student)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating student profile for user {user.id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create student profile")


@router.get("/profile/me", response_model=schemas.StudentProfile)
def get_me(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    try:
        student = db.query(models.Student).filter(models.Student.user_id == user.id).first()

        user_dict = {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "email": user.email,
        }

        student_dict = None
        if student:
            student_dict = {
                "user_id": student.user_id,
                "language": student.language,
                "current_grade": student.current_grade,
            }

        return schemas.StudentProfile(user=user_dict, student_profile=student_dict)
    except SQLAlchemyError as e:
        logger.error(f"Error fetching profile for user {user.id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")


@router.put("/profile/me", response_model=schemas.StudentProfile)
def update_me(user_data: schemas.UserCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    try:
        user_to_update = db.query(models.User).filter(models.User.id == user.id).first()

        obj_data = user_data.model_dump(exclude_unset=True)
        for key, value in obj_data.items():
            setattr(user_to_update, key, value)
        db.add(user_to_update)
        db.commit()
        db.refresh(user_to_update)
        return user_to_update
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating profile for user {user.id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not update profile")


@router.get("/{id}", response_model=schemas.StudentProfile)
def get_user(
    id: int,
    db: Session = Depends(get_db),
):
    try:
        user = db.query(models.User).filter(models.User.id == id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id: {id} does not exist",
            )
        student = db.query(models.Student).filter(models.Student.user_id == user.id).first()

        return schemas.StudentProfile(user=user, student_profile=student)
    except SQLAlchemyError as e:
        logger.error(f"Error fetching user with id {id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

