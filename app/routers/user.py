from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..database import get_db
from ..dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

# /users/
# /users


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
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
    user.password = hashed_password

    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/profile/me", response_model=schemas.User)
def create_me(profile_data: schemas.StudentCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    existing_student = db.query(models.Student).filter(models.Student.user_id == user.id).first()
    if existing_student:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student profile already exists for this user")

    new_student = models.Student(user_id=user.id, **profile_data.model_dump())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return schemas.StudentProfile(user=user, student_profile=new_student)


@router.get("/profile/me", response_model=schemas.StudentProfile)
def get_me(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    student = db.query(models.Student).filter(models.Student.user_id == user.id).first()

    # Convert to dictionaries
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


@router.put("/profile/me", response_model=schemas.User)
def update_me(user_data: schemas.UserCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.id == user.id).first()

    obj_data = user_data.model_dump(exclude_unset=True)
    for key, value in obj_data.items():
        setattr(user, key, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{id}", response_model=schemas.StudentProfile)
def get_user(
    id: int,
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {id} does not exist",
        )
    student = db.query(models.Student).filter(models.Student.user_id == user.id).first()

    return schemas.StudentProfile(user=user, student_profile=student)
