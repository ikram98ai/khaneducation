import argparse
import getpass
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, UserRole
from app.utils import hash, is_strong_password


def create_admin_user(db: Session, username: str, email: str, password: str):
    if not is_strong_password(password):
        print("Password is not strong enough. It must be at least 8 characters long and contain at least one uppercase and one lowercase letter.")
        return

    hashed_password = hash(password)
    admin_user = User(
        username=username,
        email=email,
        password=hashed_password,
        role=UserRole.ADMIN,
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    print(f"Admin user '{username}' created successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new admin user.")
    parser.add_argument("-u", "--username", required=True, help="Admin username")
    parser.add_argument("-e", "--email", required=True, help="Admin email")
    args = parser.parse_args()

    password = getpass.getpass("Enter password: ")
    password_confirm = getpass.getpass("Confirm password: ")

    if password != password_confirm:
        print("Passwords do not match.")
    else:
        db = SessionLocal()
        try:
            create_admin_user(db, args.username, args.email, password)
        finally:
            db.close()
