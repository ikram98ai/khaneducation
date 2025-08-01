# create_tables.py (run once)
from app.models import User, Subject, Lesson, Student, PracticeTask, Quiz,  QuizAttempt, StudentProgress, Notification, LessonRating, StudySession

if __name__ == "__main__":
    # Check if tables exist, create if not
    tables = [User, Subject, Lesson, Student, PracticeTask, Quiz, QuizAttempt, StudentProgress, Notification, LessonRating, StudySession]
    for table in tables:
        if not table.exists():
            print(f"Creating table {table.Meta.table_name}")
            table.create_table(wait=True)  # wait=True waits for table creation
        else:
            print(f"Table {table.Meta.table_name} already exists")
