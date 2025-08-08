import typer
import json
from app.models import UserRoleEnum, User, Subject, Lesson, Student, PracticeTask, Quiz, \
                       QuizAttempt, StudentProgress, Notification, LessonRating, StudySession
from app.utils import hash, is_strong_password
from tqdm import tqdm
app = typer.Typer()

@app.command()
def create_tables():
    """
    Create database tables.
    """
    tables = [User, Subject, Lesson, Student, PracticeTask, Quiz, QuizAttempt, StudentProgress, Notification, LessonRating, StudySession]
    for table in tables:
        if not table.exists():
            print(f"Creating table {table.Meta.table_name}")
            table.create_table(wait=True)  # wait=True waits for table creation
        else:
            print(f"Table {table.Meta.table_name} already exists")

@app.command()
def create_admin(username: str = typer.Option(..., "--username", "-u"), email: str = typer.Option(..., "--email", "-e")):
    """
    Create a new admin user.
    """
    password = typer.prompt("Enter password", hide_input=True)
    password_confirm = typer.prompt("Confirm password", hide_input=True)

    if password != password_confirm:
        print("Passwords do not match.")
        raise typer.Exit()

    if not is_strong_password(password):
        print("Password is not strong enough. It must be at least 8 characters long and contain at least one uppercase and one lowercase letter.")
        raise typer.Exit()

    hashed_password = hash(password)
    admin_user = User(
        username=username,
        email=email,
        password=hashed_password,
        role=UserRoleEnum.ADMIN.value,
    )
    admin_user.save()
    print(f"Admin user '{username}' created successfully.")

@app.command()
def list_admins():
    """
    List all admin users.
    """
    admins = User.scan(User.role == UserRoleEnum.ADMIN.value)
    for admin in admins:
        print(f"ID: {admin.id}, Username: {admin.username}, Email: {admin.email}")

@app.command()
def update_admin(user_id: str = typer.Option(..., "--id"), username: str = typer.Option(None, "--username", "-u"), email: str = typer.Option(None, "--email", "-e")):
    """
    Update an admin user's details.
    """
    try:
        admin = User.get(user_id)
        if admin.role != UserRoleEnum.ADMIN.value:
            print(f"User with ID {user_id} is not an admin.")
            raise typer.Exit()

        if username:
            admin.update(actions=[User.username.set(username)])
        if email:
            admin.update(actions=[User.email.set(email)])

        print(f"Admin with ID {user_id} updated successfully.")
    except User.DoesNotExist:
        print(f"Admin with ID {user_id} not found.")
        raise typer.Exit()

@app.command()
def delete_admin(user_id: str = typer.Option(..., "--id")):
    """
    Delete an admin user.
    """
    try:
        admin = User.get(user_id)
        if admin.role != UserRoleEnum.ADMIN.value:
            print(f"User with ID {user_id} is not an admin.")
            raise typer.Exit()

        admin.delete()
        print(f"Admin with ID {user_id} deleted successfully.")
    except User.DoesNotExist:
        print(f"Admin with ID {user_id} not found.")
        raise typer.Exit()

@app.command()
def seed_db():
    """
    Seed the database with subjects and users from seed.json.
    """
    with open("seed.json", "r") as f:
        data = json.load(f)

    # for user_data in tqdm(data.get("users", [])):
    #     password = user_data.pop("password")
    #     if not is_strong_password(password):
    #         print(f"Password for user {user_data['username']} is not strong enough. Skipping.")
    #         continue
    #     user_data["password"] = hash(password)
    #     user = User(**user_data)
    #     user.save()
    #     # print(f"Created {user_data['username']} user account")

    user = list(User.email_index.query("ikram98ai@edu.com"))[0]
    print(f"Found user {user.username}.")

    for subject_data in tqdm(data.get("subjects", [])):
        subject_info = {
            "name": subject_data.get("name"),
            "description": subject_data.get("description"),
            "grade_level": subject_data.get("grade_level"),
            "is_active": subject_data.get("is_active"),
        }
        subject = Subject(**subject_info)
        subject.save()
        for lesson_data in tqdm(subject_data.get("lessons", [])):
            lesson = Lesson(
                subject_id=subject.id,
                instructor_id=user.id,
                **lesson_data
            )
            lesson.save()
        print(f"Created {subject.name} subject")
        break


    print("Database seeded successfully.")

@app.command()
def update_all_passwords():
    """
    Update all users' passwords to 'Abc123()'.
    """
    new_password = "Abc123()"
    if not is_strong_password(new_password):
        print(f"The new password is not strong enough.")
        raise typer.Exit()

    hashed_password = hash(new_password)
    users = User.scan()
    for user in users:
        user.update(actions=[User.password.set(hashed_password)])
    print("All user passwords updated successfully.")

if __name__ == "__main__":
    app()
