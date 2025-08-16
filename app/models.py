# app/models.py
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute, BooleanAttribute, ListAttribute, MapAttribute, JSONAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection, KeysOnlyProjection, IncludeProjection
from .config import settings
import enum
import uuid
from datetime import datetime, timezone
from typing import List


class UserRoleEnum(enum.Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    CONTENT_MANAGER = "content_manager"
    STAFF = "staff"
    ADMIN = "admin"


class LanguageChoicesEnum(enum.Enum):
    AR = "Arabic"
    EN = "English"
    PS = "Pashto"
    FA = "Persian"
    UR = "Urdu"


class LessonStatusEnum(enum.Enum):
    DRAFT = "draft"
    VERIFIED = "verified"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    PENDING = "pending"
    FAILED = "failed"


class DifficultyLevelEnum(enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionTypeEnum(enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    MULTIPLE_OPTION = "multiple_option"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"


# --- Base Model ---
class BaseModel(Model):
    class Meta:
        region = settings.aws_region
        # host = settings.dynamodb_endpoint_url
        # aws_access_key_id = settings.aws_access_key_id
        # aws_secret_access_key = settings.aws_secret_access_key
        billing_mode = "PAY_PER_REQUEST"

    created_at = UTCDateTimeAttribute(default_for_new=lambda: datetime.now(timezone.utc))
    updated_at = UTCDateTimeAttribute(default=lambda: datetime.now(timezone.utc))

    def save(self, **kwargs):
        """Override save to update the updated_at timestamp"""
        self.updated_at = datetime.now(timezone.utc)
        super().save(**kwargs)


# --- Define Global Secondary Indexes (GSI) ---
class UserEmailIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "email-index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()  # More efficient for lookups

    email = UnicodeAttribute(hash_key=True)


class UsernameIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "username-index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = KeysOnlyProjection()

    username = UnicodeAttribute(hash_key=True)


class UserRoleIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "role-index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = KeysOnlyProjection()

    role = UnicodeAttribute(hash_key=True)
    created_at = UTCDateTimeAttribute(range_key=True)


# --- Main Models ---
class User(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "khaneducation_users"

    id = UnicodeAttribute(hash_key=True, default_for_new=lambda: str(uuid.uuid4()))

    username = UnicodeAttribute()
    first_name = UnicodeAttribute(null=True)
    last_name = UnicodeAttribute(null=True)
    email = UnicodeAttribute()
    password = UnicodeAttribute()  # Should be hashed
    role = UnicodeAttribute(default=UserRoleEnum.STUDENT.value)
    is_active = BooleanAttribute(default=True)
    last_login = UTCDateTimeAttribute(null=True)
    email_verified = BooleanAttribute(default=False)

    # Define GSIs
    email_index = UserEmailIndex()
    username_index = UsernameIndex()
    role_index = UserRoleIndex()

    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username or self.email.split("@")[0]


class SubjectGradeLevelIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "grade-level-index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    grade_level = NumberAttribute(hash_key=True)


class Subject(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "khaneducation_subjects"

    id = UnicodeAttribute(hash_key=True, default_for_new=lambda: str(uuid.uuid4()))

    name = UnicodeAttribute()
    description = UnicodeAttribute(null=True)
    grade_level = NumberAttribute()
    is_active = BooleanAttribute(default=True)
    prerequisites = ListAttribute(of=UnicodeAttribute, null=True)  # List of subject IDs

    # GSI for querying by grade level and language
    grade_level_index = SubjectGradeLevelIndex()


class LessonSubjectIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "subject-index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    subject_id = UnicodeAttribute(hash_key=True)
    id = UnicodeAttribute(range_key=True)  # Lesson ID as range key


class LessonSubjectLanguageIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "subject-language-index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = IncludeProjection(["id","language","title","order_in_subject","subject_id"])  # Only project selected attrs

    subject_id = UnicodeAttribute(hash_key=True)
    language = UnicodeAttribute(range_key=True)


class LessonInstructorIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "instructor-index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    instructor_id = UnicodeAttribute(hash_key=True)
    created_at = UTCDateTimeAttribute(range_key=True)


class LessonStatusIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "status-index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    status = UnicodeAttribute(hash_key=True)
    created_at =  UTCDateTimeAttribute(range_key=True)


class Lesson(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "khaneducation_lessons"

    id = UnicodeAttribute(hash_key=True, default_for_new=lambda: str(uuid.uuid4()))

    subject_id = UnicodeAttribute()
    instructor_id = UnicodeAttribute()
    title = UnicodeAttribute()
    language = UnicodeAttribute()
    content = UnicodeAttribute()
    summary = UnicodeAttribute(null=True)  # Brief lesson summary
    learning_objectives = ListAttribute(of=UnicodeAttribute, null=True)
    status = UnicodeAttribute(default=LessonStatusEnum.DRAFT.value)
    difficulty = UnicodeAttribute(default=DifficultyLevelEnum.MEDIUM.value)
    estimated_duration_minutes = NumberAttribute(null=True)
    order_in_subject = NumberAttribute(null=True)  # For sequencing lessons
    verified_at = UTCDateTimeAttribute(null=True)
    verified_by = UnicodeAttribute(null=True)  # User ID who verified
    tags = ListAttribute(of=UnicodeAttribute, null=True)

    # GSIs for efficient querying
    subject_index = LessonSubjectIndex()
    subject_and_language_index = LessonSubjectLanguageIndex()
    instructor_index = LessonInstructorIndex()
    status_index = LessonStatusIndex()




class StudentByGradeAndLanguageIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "student-grade-language-index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    current_grade = NumberAttribute(hash_key=True)
    language = UnicodeAttribute(range_key=True)


class EnrollmentAttribute(MapAttribute):
    subject_id = UnicodeAttribute()
    enrolled_at = UTCDateTimeAttribute()
    status = UnicodeAttribute(default="active")  # active, completed, dropped


class Student(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "khaneducation_students"

    user_id = UnicodeAttribute(hash_key=True)  # Link to User
    current_grade = NumberAttribute(range_key=True)  # Current grade level
    language = UnicodeAttribute(default=LanguageChoicesEnum.EN.value)
    date_of_birth = UTCDateTimeAttribute(null=True)
    parent_email = UnicodeAttribute(null=True)
    learning_preferences = JSONAttribute(null=True)  # Store learning style preferences

    # Use proper list attribute for enrollments
    enrollments = ListAttribute(of=EnrollmentAttribute, null=True)
    grade_language_index = StudentByGradeAndLanguageIndex()

    def add_enrollment(self, subject_id: str, enrolled_at: datetime = None, status: str = "active"):
        """Add a new enrollment"""
        if not enrolled_at:
            enrolled_at = datetime.now(timezone.utc)

        if not self.enrollments:
            self.enrollments = []

        # Check if already enrolled
        existing_enrollment = next((e for e in self.enrollments if e.subject_id == subject_id), None)
        if existing_enrollment:
            existing_enrollment.status = status
            return

        enrollment = EnrollmentAttribute()
        enrollment.subject_id = subject_id
        enrollment.enrolled_at = enrolled_at
        enrollment.status = status

        self.enrollments.append(enrollment)

    def get_active_enrollments(self) -> List[EnrollmentAttribute]:
        """Get all active enrollments"""
        if not self.enrollments:
            return []
        return [e for e in self.enrollments if e.status == "active"]


class PracticeTaskByLessonIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "practice-task-lesson-index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    lesson_id = UnicodeAttribute(hash_key=True)


class PracticeTask(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "khaneducation_practice_tasks"

    id = UnicodeAttribute(hash_key=True, default_for_new=lambda: str(uuid.uuid4()))

    lesson_id = UnicodeAttribute(range_key=True)
    lesson_title = UnicodeAttribute()
    content = UnicodeAttribute()
    solution = UnicodeAttribute()
    instructions = UnicodeAttribute(null=True)
    difficulty = UnicodeAttribute(default=DifficultyLevelEnum.MEDIUM.value)
    ai_generated = BooleanAttribute(default=True)
    lesson_index = PracticeTaskByLessonIndex()


class QuizQuestionAttribute(MapAttribute):
    question_id = UnicodeAttribute()
    question_text = UnicodeAttribute()
    question_type = UnicodeAttribute()
    options = ListAttribute(of=UnicodeAttribute, null=True)
    correct_answer = UnicodeAttribute(null=True)


class QuizResponseAttribute(MapAttribute):
    question_id = UnicodeAttribute()
    student_answer = UnicodeAttribute()
    is_correct = BooleanAttribute()


class QuizByLessonStudentIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "quiz-lesson-student-index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    lesson_id = UnicodeAttribute(hash_key=True)
    student_id = UnicodeAttribute(range_key=True)


class QuizBySubjectStudentIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "quiz-subject-student-index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    subject_id = UnicodeAttribute(hash_key=True)
    student_id = UnicodeAttribute(range_key=True)

class QuizByStudentIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "quiz-student-index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    student_id = UnicodeAttribute(hash_key=True)

QUIZ_PASSING_SCORE = 70


class Quiz(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "khaneducation_quizzes"

    id = UnicodeAttribute(hash_key=True, default_for_new=lambda: str(uuid.uuid4()))
    student_id = UnicodeAttribute()
    subject_id = UnicodeAttribute()
    lesson_id = UnicodeAttribute()
    lesson_title = UnicodeAttribute()
    quiz_version = NumberAttribute(default=1)
    start_time = UTCDateTimeAttribute(default_for_new=lambda: datetime.now(timezone.utc))
    end_time = UTCDateTimeAttribute(null=True)
    time_taken_minutes = NumberAttribute(null=True)
    ai_feedback = UnicodeAttribute(null=True)
    score = NumberAttribute(null=True)
    passed = BooleanAttribute(default=False)
    cheating_detected = BooleanAttribute(default=False)

    # Use proper list attribute for questions
    quiz_questions = ListAttribute(of=QuizQuestionAttribute, null=True)
    # Use proper list attribute for responses
    responses = ListAttribute(of=QuizResponseAttribute, null=True)

    lesson_student_index = QuizByLessonStudentIndex()
    student_index = QuizByStudentIndex()
    subject_student_index = QuizBySubjectStudentIndex()

    def add_question(self, question_text: str, question_type: str, options: List[str] = None, correct_answer: str = None):
        """Add a question to the quiz"""
        if not self.quiz_questions:
            self.quiz_questions = []

        question = QuizQuestionAttribute()
        question.question_id = str(uuid.uuid4())
        question.question_text = question_text
        question.question_type = question_type
        question.options = options
        question.correct_answer = correct_answer

        self.quiz_questions.append(question)

    def add_response(self, question_id: str, student_answer: str, is_correct: bool):
        """Add a response to the quiz attempt"""
        if not self.responses:
            self.responses = []

        response = QuizResponseAttribute()
        response.question_id = question_id
        response.student_answer = student_answer
        response.is_correct = is_correct

        self.responses.append(response)

    def calculate_score(self):
        """Calculate the total score and percentage"""
        if not self.responses:
            self.score = 0
            return

        # Get quiz to calculate percentage
        total_correct = sum([int(r.is_correct) for r in self.responses])
        self.score = (total_correct / len(self.responses)) * 100

        if self.score >= QUIZ_PASSING_SCORE:
            self.passed = True
        else:
            self.passed = False

    def finish_quiz(self):
        """Mark the attempt as finished"""
        self.end_time = datetime.now(timezone.utc)
        if self.start_time:
            time_diff = self.end_time - self.start_time
            self.time_taken_minutes = round(time_diff.total_seconds() / 60, 2)
        self.calculate_score()

# --- Additional Models for Enhanced Functionality ---


class Notification(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "khaneducation_notifications"

    id = UnicodeAttribute(hash_key=True, default_for_new=lambda: str(uuid.uuid4()))

    user_id = UnicodeAttribute()
    title = UnicodeAttribute()
    message = UnicodeAttribute()
    notification_type = UnicodeAttribute()  # info, warning, success, error
    is_read = BooleanAttribute(default=False)
    action_url = UnicodeAttribute(null=True)
    expires_at = UTCDateTimeAttribute(null=True)
