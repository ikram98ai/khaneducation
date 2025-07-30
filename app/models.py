# app/models.py
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute, BooleanAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from .config import settings
import enum, uuid
import json
from datetime import datetime

class UserRoleEnum(enum.Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    CONTENT_MANAGER = "content_manager"
    STAFF = "staff"
    ADMIN = "admin"

class LanguageChoicesEnum(enum.Enum):
    EN = "English"
    FR = "French"
    PS = "Pashto"
    ES = "Spanish"
    AR = "Arabic"
    FA = "Persian"
    UR = "Urdu"

class LessonStatusEnum(enum.Enum):
    DRAFT = "DR"
    VERIFIED = "VE"

class DifficultyLevelEnum(enum.Enum):
    EASY = "EA"
    MEDIUM = "ME"
    HARD = "HA"

# --- Define Global Secondary Indexes (GSI) ---
class UserEmailIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'email-index'
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection() # Projects all attributes

    email = UnicodeAttribute(hash_key=True)

class UsernameIndex(GlobalSecondaryIndex):
     class Meta:
         index_name = 'username-index'
         read_capacity_units = 1
         write_capacity_units = 1
         projection = AllProjection()

     username = UnicodeAttribute(hash_key=True)

class BaseModel(Model):
    class Meta:
        region = settings.aws_region
        host = settings.dynamodb_endpoint_url
        aws_access_key_id = settings.aws_access_key_id
        aws_secret_access_key = settings.aws_secret_access_key
    
    id = UnicodeAttribute(hash_key=True, default_for_new=lambda: str(uuid.uuid4()))


class User(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = 'users'
    
    # Attributes
    username = UnicodeAttribute(null=True) # Make nullable if needed
    first_name = UnicodeAttribute(null=True)
    last_name = UnicodeAttribute(null=True)
    email = UnicodeAttribute() # Assuming email is required
    password = UnicodeAttribute() 
    role = UnicodeAttribute(default=UserRoleEnum.STUDENT.value)
    created_at = UTCDateTimeAttribute(default_for_new=None) # PynamoDB handles default timestamps

    # Define GSI
    email_index = UserEmailIndex()
    username_index = UsernameIndex()

# Subject (simplified)
class Subject(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = 'subjects'

    name = UnicodeAttribute()
    description = UnicodeAttribute(null=True)
    grade_level = NumberAttribute()
    language = UnicodeAttribute(default=LanguageChoicesEnum.EN.value)

# Lesson (using composite key)
class Lesson(BaseModel):
     class Meta(BaseModel.Meta):
         table_name = 'lessons'

     subject_id = UnicodeAttribute()
     instructor_id = UnicodeAttribute() # Link to User ID
     title = UnicodeAttribute()
     content = UnicodeAttribute()
     status = UnicodeAttribute(default=LessonStatusEnum.DRAFT.value)
     created_at = UTCDateTimeAttribute(default_for_new=None)
     verified_at = UTCDateTimeAttribute(null=True)

# Student
class Student(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = 'students'

    # Primary Key (likely the User ID it's linked to)
    user_id = UnicodeAttribute()
    language = UnicodeAttribute(default=LanguageChoicesEnum.EN.value)
    current_grade = NumberAttribute()
    # Store enrollments as a list of dicts: [{"subject_id": ..., "enrolled_at": ...}, ...]
    enrollments = UnicodeAttribute(null=True)  # Store as JSON string

    def add_enrollment(self, subject_id, enrolled_at):
        enrollments = []
        if self.enrollments:
            enrollments = json.loads(self.enrollments)
        enrollments.append({
            "subject_id": subject_id,
            "enrolled_at": enrolled_at.isoformat() if isinstance(enrolled_at, datetime) else enrolled_at
        })
        self.enrollments = json.dumps(enrollments)


# PracticeTask
class PracticeTask(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = 'practice_tasks'

    
    lesson_id = UnicodeAttribute() # Link to Lesson (subject_id can be derived if needed)
    content = UnicodeAttribute()
    difficulty = UnicodeAttribute(default=DifficultyLevelEnum.MEDIUM.value)
    ai_generated = BooleanAttribute(default=True)
    created_at = UTCDateTimeAttribute(default_for_new=None)

# Quiz
class Quiz(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = 'quizzes'

    lesson_id = UnicodeAttribute() # Link to Lesson
    version_number = NumberAttribute(default=1)
    ai_generated = BooleanAttribute(default=True)
    created_at = UTCDateTimeAttribute(default_for_new=None)
    quiz_questions = UnicodeAttribute(null=True) # Store JSON or serialized list of question IDs

# QuizAttempt (composite key)
class QuizAttempt(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = 'quiz_attempts'

    student_id = UnicodeAttribute()
    # Unique ID for the attempt
    quiz_id = UnicodeAttribute() # Link to Quiz
    start_time = UTCDateTimeAttribute(default_for_new=None)
    end_time = UTCDateTimeAttribute(null=True)
    score = NumberAttribute(null=True)
    passed = BooleanAttribute(default=False)
    cheating_detected = BooleanAttribute(default=False)

# StudentResponse
class StudentResponse(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = 'student_responses'
    
    attempt_id = UnicodeAttribute() # Link to QuizAttempt
    question_id = UnicodeAttribute() # Link to QuizQuestion
    student_answer = UnicodeAttribute()
    is_correct = BooleanAttribute()
