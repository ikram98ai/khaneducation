# app/routers/auth.py
from fastapi import APIRouter, Depends, status, HTTPException
# Remove: from sqlalchemy.orm import Session
# Remove: from sqlalchemy.exc import SQLAlchemyError
import logging
# Remove: from .. import database # No more SQLAlchemy session
from .. import schemas # Keep schemas
# Remove: from .. import models # Remove SQLAlchemy models
from ..models import User # Import PynamoDB User model
from .. import utils, dependencies # Keep utils and dependencies
# Remove: from ..database import get_db # No more dependency

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Authentication"])

@router.post("/login", response_model=schemas.Token)
def login(
    user_credentials: schemas.UserLogin,
    # db: Session = Depends(database.get_db), # Remove SQLAlchemy dependency
):
    # try: # Remove outer try/except for SQLAlchemyError
        # --- Fetch user using PynamoDB ---
        # Requires GSI on email for efficient lookup
        try:
            # Assuming User model has email_index GSI
            matching_users = list(User.email_index.query(user_credentials.email))
            user = matching_users[0] if matching_users else None
        except Exception as e: # Catch PynamoDB errors
            logger.error(f"Database error during user lookup for email {user_credentials.email}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

        if not user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

        if not utils.verify(user_credentials.password, user.password):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

        # --- Create access token ---
        access_token = dependencies.create_access_token(
            data={
                "user_id": user.id, # Assuming user.id is the hash key
                "email": user.email,
                "username": user.username,
                "role": user.role, # This is the string value
            }
        )
        return {"access_token": access_token, "token_type": "bearer"}
    # except SQLAlchemyError as e: # Remove SQLAlchemy specific exception
    #     logger.error(f"Database error during login for email {user_credentials.email}: {e}")
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    # except Exception as e: # Keep general exception handling if needed
    #     logger.error(f"An unexpected error occurred during login: {e}")
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")
