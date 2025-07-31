# app/routers/auth.py
from fastapi import APIRouter, status, HTTPException

import logging
from .. import schemas 
from ..models import User
from .. import utils, dependencies

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=schemas.Token)
def login(
    user_credentials: schemas.UserLogin,
):
    try:
        matching_user = next(User.email_index.query(user_credentials.email), None)
        user = User.get(matching_user.id)
    except Exception as e:
        logger.error(f"Database error during user lookup for email {user_credentials.email}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

    if not user:
        print("No user found with the provided email.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    # --- Create access token ---
    access_token = dependencies.create_access_token(
        data={
            "user_id": user.id,  # Assuming user.id is the hash key
            "email": user.email,
            "username": user.username,
            "role": user.role,  # This is the string value
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}
