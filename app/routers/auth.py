from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from .. import database, schemas, models, utils, dependencies

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=schemas.Token)
def login(
    user_credentials: schemas.UserLogin,
    db: Session = Depends(database.get_db),
):
    try:
        user = db.query(models.User).filter(models.User.email == user_credentials.email).first()

        if not user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

        if not utils.verify(user_credentials.password, user.password):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

        access_token = dependencies.create_access_token(
            data={
                "user_id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role.value,
            }
        )

        return {"access_token": access_token, "token_type": "bearer"}
    except SQLAlchemyError as e:
        logger.error(f"Database error during login for email {user_credentials.email}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    # except Exception as e:
    #     logger.error(f"An unexpected error occurred during login: {e}")
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")
