from passlib.context import CryptContext
import re

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return pwd_context.hash(password)


def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def is_strong_password(password: str) -> bool:
    """Check password strength."""
    if (
        len(password) < 8
        or not re.search(r"[A-Z]", password)
        or not re.search(r"[a-z]", password)
        or not re.search(r"[0-9]", password)
        or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
    ):
        return False
    return True
