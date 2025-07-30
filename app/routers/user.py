# app/routers/user.py
from fastapi import status, HTTPException, Depends, APIRouter

# Remove: from sqlalchemy.orm import Session
# Remove: from sqlalchemy.exc import SQLAlchemyError
from ..models import User, Student, Enrollment, Subject  # Import PynamoDB models
from .. import schemas, utils

# Remove: from ..database import get_db
from ..dependencies import get_current_user

# Remove: from .. import models # Remove SQLAlchemy models
import logging
from pynamodb.transactions import TransactWrite

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])
# --- Atomic User Creation with Transaction (PynamoDB) ---


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
def create_user(user: schemas.UserCreate):
    # Remove: db: Session = Depends(get_db)
    # try: # Remove outer SQLAlchemy try/except
    try:
        # Check email (assuming email_index GSI exists)
        email_users = list(User.email_index.query(user.email))
        if email_users:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered.")

        # Check username (assuming username_index GSI exists)
        username_users = list(User.username_index.query(user.username))
        if username_users:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username is already taken.")

    except Exception as e:  # Catch PynamoDB errors during lookup
        logger.error(f"Error checking for existing user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    # --- End Check Existing User ---

    if not utils.is_strong_password(user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Password must be at least 8 characters long, and include at least one "
                "uppercase letter, one lowercase letter, one digit, and one special character."
            ),
        )

    # hash the password
    hashed_password = utils.hash(user.password)
    user_data = user.model_dump()
    user_data["password"] = hashed_password

    # --- Atomic transaction using PynamoDB TransactWrite ---
    try:
        new_user = User(**user_data)
        with TransactWrite() as transaction:
            transaction.save(new_user)
            # Add more transactional writes here if needed (e.g., create related records)
            # Example:
            # transaction.save(OtherModel(...))

    except Exception as e:  # Catch PynamoDB transaction errors
        logger.error(f"Error creating user (transaction): {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create user")
    # --- End Create User ---

    return new_user

    # except SQLAlchemyError as e: # Remove
    #     db.rollback()
    #     logger.error(f"Error creating user: {e}")
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create user")


# --- Example: Create Student Profile ---
@router.post("/profile/me", response_model=schemas.StudentProfile)
def create_me(profile_data: schemas.StudentCreate, user: schemas.User = Depends(get_current_user)):  # Use User schema from token
    # Remove: db: Session = Depends(get_db)
    # try:
    try:
        # Check if student profile already exists
        existing_student = Student.get(user.id)  # Assuming user.id is the hash key for Student
        if existing_student:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student profile already exists for this user")
    except Student.DoesNotExist:
        # This is expected if the profile doesn't exist
        pass
    except Exception as e:
        logger.error(f"Error checking student profile for user {user.id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

    # --- Create new student profile ---
    try:
        student_data = profile_data.model_dump()
        student_data["user_id"] = user.id  # Link to user
        new_student = Student(**student_data)
        new_student.save()

        # --- Find matching subjects and enroll the student ---
        # This requires querying Subject by grade_level and language
        # Requires GSI on Subject for efficient querying by these attributes
        try:
            matching_subjects = list(
                Subject.grade_language_index.query(
                    profile_data.current_grade,  # Assuming composite GSI: grade (hash), language (range)
                    filter_condition=Subject.language == profile_data.language.value,  # Or just == profile_data.language if stored as string
                )
            )
            # Or if separate GSIs:
            # matching_subjects = list(Subject.scan(
            #     filter_condition=(Subject.grade_level == profile_data.current_grade) & (Subject.language == profile_data.language.value)
            # ))
            # Scanning is inefficient, prefer GSI.

            for subject in matching_subjects:
                # Create enrollment
                # Assuming Enrollment PK is student_id (hash) + subject_id (range) or a unique ID
                enrollment_data = {
                    "student_id": user.id,
                    "subject_id": subject.id,
                    # 'enrolled_at': datetime.now(timezone.utc) # If needed
                }
                enrollment = Enrollment(**enrollment_data)
                enrollment.save()
        except Exception as e:
            # Log error but don't fail student creation necessarily?
            logger.error(f"Error enrolling student {user.id} in matching subjects: {e}")
            # Optionally raise or continue

        # --- Return profile data ---
        # Construct the response schema
        return schemas.StudentProfile(user=user, student_profile=new_student)

    except Exception as e:  # Catch errors during student creation or enrollment
        # db.rollback() # Not directly applicable
        logger.error(f"Error creating student profile for user {user.id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create student profile")


# except SQLAlchemyError as e: # Remove
#     db.rollback()
#     logger.error(f"Error creating student profile for user {user.id}: {e}")
#     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create student profile")

# --- Other endpoints like get_me, update_me, get_user ---
# Follow similar patterns:
# 1. Remove db dependency.
# 2. Replace SQLAlchemy queries (db.query(...).filter(...).first()) with PynamoDB .get() or .query()/.scan().
# 3. Handle PynamoDB exceptions (DoesNotExist, PutError, UpdateError, etc.).
# 4. Construct response schemas from PynamoDB model data or pass models directly if compatible.
# 5. Remove SQLAlchemy-specific exception handling.
