from fastapi import status, HTTPException, Depends, APIRouter
from ..models import User, Student
from .. import schemas, utils, crud
from ..dependencies import get_current_user
import logging
from pynamodb.transactions import TransactWrite
from pynamodb.connection import Connection
import enum
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
def create_user(user: schemas.UserCreate):
    try:
        email_users = crud.crud_user.get_by_email(email=user.email)
        if email_users:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered.")

        username_users = crud.crud_user.get_by_username(username=user.username)
        if username_users:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username is already taken.")

    except Exception as e:
        logger.error(f"Error checking for existing user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

    if not utils.is_strong_password(user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Password must be at least 8 characters long, and include at least one "
                "uppercase letter, one lowercase letter, one digit, and one special character."
            ),
        )

    hashed_password = utils.hash(user.password)
    user_data = user.model_dump()
    user_data["password"] = hashed_password

    # Convert Enum to string
    if isinstance(user_data.get("role"), enum.Enum):
        user_data["role"] = user_data["role"].value

    try:
        new_user = User(**user_data)
        # Create a connection for the transaction
        conn = Connection()
        with TransactWrite(connection=conn) as transaction:
            transaction.save(new_user)

    except Exception as e:
        logger.error(f"Error creating user (transaction): {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create user")

    return new_user


@router.post("/profile/me", response_model=schemas.StudentProfile)
def create_me(profile_data: schemas.StudentCreate, user: schemas.User = Depends(get_current_user)):
    try:
        existing_student = crud.crud_student.get(hash_key=user.id)
        if existing_student:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student profile already exists for this user")
    except Student.DoesNotExist:
        pass
    except Exception as e:
        logger.error(f"Error checking student profile for user {user.id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

    try:
        student_data = profile_data.model_dump()
        student_data["user_id"] = user.id
        new_student = Student(**student_data)
        new_student.save()

        try:
            matching_subjects = crud.crud_subject.get_by_grade_and_language(
                grade_level=profile_data.current_grade, 
                language=profile_data.language.value
            )

            for subject in matching_subjects:
                new_student.add_enrollment(subject_id=subject.id)
            new_student.save()

        except Exception as e:
            logger.error(f"Error enrolling student {user.id} in matching subjects: {e}")

        return schemas.StudentProfile(user=user, student_profile=new_student)

    except Exception as e:
        logger.error(f"Error creating student profile for user {user.id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create student profile")


@router.get("/me", response_model=schemas.User)
def get_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=schemas.User)
def update_me(user_update: schemas.UserUpdate, current_user: schemas.User = Depends(get_current_user)):
    try:
        user_to_update = crud.crud_user.get(hash_key=current_user.id)
    except User.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except Exception as e:
        logger.error(f"Error fetching user {current_user.id} for update: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user_to_update, key, value)

    try:
        user_to_update.save()
        return user_to_update
    except Exception as e:
        logger.error(f"Error updating user {current_user.id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not update user")


@router.get("/{id}", response_model=schemas.User)
def get_user(id: str):
    try:
        user = crud.crud_user.get(hash_key=id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {id} does not exist")
        return user
    except Exception as e:
        logger.error(f"Error fetching user {id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")