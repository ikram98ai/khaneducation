from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

from .models import User, Student, UserRoleEnum
from .config import settings
from .schemas import User as UserSchema, TokenData, Student as StudentSchema

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")
        if id is None:
            raise credentials_exception
        token_data = TokenData(id=id)
    except JWTError:
        raise credentials_exception

    return token_data


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserSchema:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        user_id: int = payload.get("user_id")
        username: str = payload.get("username")

        if email is None or user_id is None or username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Get user from PynamoDB
    try:
        user = User.get(hash_key=user_id)
    except User.DoesNotExist:
        raise credentials_exception

    return UserSchema(
        id=user.id,
        username=user.username,
        first_name=getattr(user, "first_name", ""),
        last_name=getattr(user, "last_name", ""),
        email=user.email,
        role=user.role,
    )


async def get_current_student(user: UserSchema = Depends(get_current_user)) -> StudentSchema:
    if user.role != UserRoleEnum.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student profile required",
        )

    # Verify student profile exists in PynamoDB
    student = None
    for s in Student.query(user.id):
        student = s
        break

    if not student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Complete your student profile first",
        )

    return student


async def get_current_admin(current_user: UserSchema = Depends(get_current_user)) -> UserSchema:
    if current_user.role not in [UserRoleEnum.ADMIN, UserRoleEnum.STAFF]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


async def get_content_admin(current_user: UserSchema = Depends(get_current_user)) -> UserSchema:
    if current_user.role not in [UserRoleEnum.ADMIN, UserRoleEnum.CONTENT_MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Content management privileges required",
        )
    return current_user
