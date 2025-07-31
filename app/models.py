# app/models.py
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute, BooleanAttribute, ListAttribute, MapAttribute, JSONAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection, KeysOnlyProjection
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
    EN = "English"
    FR = "French"
    PS = "Pashto"
    ES = "Spanish"
    AR = "Arabic"
    FA = "Persian"
    UR = "Urdu"


class LessonStatusEnum(enum.Enum):
    DRAFT = "draft"
    VERIFIED = "verified"
    PUBLISHED = "published"
    ARCHIVED = "archived"


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


# --- Custom Attribute Classes ---
class EnrollmentAttribute(MapAttribute):
    subject_id = UnicodeAttribute()
    enrolled_at = UTCDateTimeAttribute()
    status = UnicodeAttribute(default="active")  # active, completed, dropped


class QuizQuestionAttribute(MapAttribute):
    question_id = UnicodeAttribute()
    question_text = UnicodeAttribute()
    question_type = UnicodeAttribute()
    options = ListAttribute(of=UnicodeAttribute, null=True)
    correct_answer = UnicodeAttribute(null=True)
    points = NumberAttribute(default=1)


class QuizResponseAttribute(MapAttribute):
    question_id = UnicodeAttribute()
    student_answer = UnicodeAttribute()
    is_correct = BooleanAttribute()
    points_earned = NumberAttribute(default=0)


# --- Define Global Secondary Indexes (GSI) ---
class UserEmailIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "email-index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = KeysOnlyProjection()  # More efficient for lookups

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


class SubjectGradeLevelIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "grade-level-index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    grade_level = NumberAttribute(hash_key=True)
    language = UnicodeAttribute(range_key=True)


class LessonSubjectIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "subject-index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    subject_id = UnicodeAttribute(hash_key=True)
    id = UnicodeAttribute(range_key=True)  # Lesson ID as range key


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
    created_at = UTCDateTimeAttribute(range_key=True)


class StudentProgressLessonIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "lesson-progress-index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    lesson_id = UnicodeAttribute(hash_key=True)
    last_accessed = UTCDateTimeAttribute(range_key=True)


class QuizAttemptStudentIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "student-attempts-index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    student_id = UnicodeAttribute(hash_key=True)
    id = UTCDateTimeAttribute(range_key=True)

class StudentByGradeAndLanguageIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "student-grade-language-index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()
    current_grade = NumberAttribute(hash_key=True)
    language = UnicodeAttribute(range_key=True)

class PracticeTaskByLessonIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "practice-task-lesson-index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()
    lesson_id = UnicodeAttribute(hash_key=True)

class QuizByLessonIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "quiz-lesson-index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()
    lesson_id = UnicodeAttribute(hash_key=True)

class QuizAttemptByStudentAndQuizIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "quiz-attempt-student-quiz-index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()
    student_id = UnicodeAttribute(hash_key=True)
    quiz_id = UnicodeAttribute(range_key=True)


# --- Base Model ---
class BaseModel(Model):
    class Meta:
        region = settings.aws_region
        host = settings.dynamodb_endpoint_url
        aws_access_key_id = settings.aws_access_key_id
        aws_secret_access_key = settings.aws_secret_access_key

    id = UnicodeAttribute(hash_key=True, default_for_new=lambda: str(uuid.uuid4()))
    created_at = UTCDateTimeAttribute(default_for_new=lambda: datetime.now(timezone.utc))
    updated_at = UTCDateTimeAttribute(default=lambda: datetime.now(timezone.utc))

    def save(self, **kwargs):
        """Override save to update the updated_at timestamp"""
        self.updated_at = datetime.now(timezone.utc)
        super().save(**kwargs)


# --- Main Models ---
class User(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "users"

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


class Subject(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "subjects"

    name = UnicodeAttribute()
    description = UnicodeAttribute(null=True)
    grade_level = NumberAttribute()
    language = UnicodeAttribute(default=LanguageChoicesEnum.EN.value)
    is_active = BooleanAttribute(default=True)
    prerequisites = ListAttribute(of=UnicodeAttribute, null=True)  # List of subject IDs

    # GSI for querying by grade level and language
    grade_level_index = SubjectGradeLevelIndex()


class Lesson(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "lessons"

    subject_id = UnicodeAttribute()  # Subject ID as hash key
    instructor_id = UnicodeAttribute()
    title = UnicodeAttribute()
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
    instructor_index = LessonInstructorIndex()
    status_index = LessonStatusIndex()


class Student(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "students"

    user_id = UnicodeAttribute()  # Link to User
    language = UnicodeAttribute(default=LanguageChoicesEnum.EN.value)
    current_grade = NumberAttribute()
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


class PracticeTask(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "practice_tasks"

    lesson_id = UnicodeAttribute()
    title = UnicodeAttribute()
    content = UnicodeAttribute()
    instructions = UnicodeAttribute(null=True)
    difficulty = UnicodeAttribute(default=DifficultyLevelEnum.MEDIUM.value)
    estimated_time_minutes = NumberAttribute(null=True)
    ai_generated = BooleanAttribute(default=True)
    points_possible = NumberAttribute(default=10)
    is_active = BooleanAttribute(default=True)
    lesson_index = PracticeTaskByLessonIndex()


class Quiz(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "quizzes"

    lesson_id = UnicodeAttribute()
    title = UnicodeAttribute()
    description = UnicodeAttribute(null=True)
    version_number = NumberAttribute(default=1)
    time_limit_minutes = NumberAttribute(null=True)
    passing_score = NumberAttribute(default=70)  # Percentage
    max_attempts = NumberAttribute(default=3)
    ai_generated = BooleanAttribute(default=True)
    is_active = BooleanAttribute(default=True)

    # Use proper list attribute for questions
    quiz_questions = ListAttribute(of=QuizQuestionAttribute, null=True)
    lesson_index = QuizByLessonIndex()

    def add_question(self, question_text: str, question_type: str, options: List[str] = None, correct_answer: str = None, points: int = 1):
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

    @property
    def total_points(self) -> int:
        """Calculate total points for the quiz"""
        if not self.quiz_questions:
            return 0
        return sum(q.points for q in self.quiz_questions)


class QuizAttempt(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "quiz_attempts"

    student_id = UnicodeAttribute()
    quiz_id = UnicodeAttribute()
    attempt_number = NumberAttribute()  # Track attempt count
    start_time = UTCDateTimeAttribute(default_for_new=lambda: datetime.now(timezone.utc))
    end_time = UTCDateTimeAttribute(null=True)
    score = NumberAttribute(null=True)
    percentage_score = NumberAttribute(null=True)
    passed = BooleanAttribute(default=False)
    cheating_detected = BooleanAttribute(default=False)
    time_taken_minutes = NumberAttribute(null=True)

    # Use proper list attribute for responses
    responses = ListAttribute(of=QuizResponseAttribute, null=True)

    # GSI for querying student attempts
    student_index = QuizAttemptStudentIndex()
    student_quiz_index = QuizAttemptByStudentAndQuizIndex()

    def add_response(self, question_id: str, student_answer: str, is_correct: bool, points_earned: int = 0):
        """Add a response to the quiz attempt"""
        if not self.responses:
            self.responses = []

        response = QuizResponseAttribute()
        response.question_id = question_id
        response.student_answer = student_answer
        response.is_correct = is_correct
        response.points_earned = points_earned

        self.responses.append(response)

    def calculate_score(self):
        """Calculate the total score and percentage"""
        if not self.responses:
            self.score = 0
            self.percentage_score = 0
            return

        total_points = sum(r.points_earned for r in self.responses)
        self.score = total_points

        # Get quiz to calculate percentage
        try:
            quiz = Quiz.get(self.quiz_id)
            if quiz.total_points > 0:
                self.percentage_score = round((total_points / quiz.total_points) * 100, 2)
                self.passed = self.percentage_score >= quiz.passing_score
        except Quiz.DoesNotExist:
            self.percentage_score = 0

    def finish_attempt(self):
        """Mark the attempt as finished"""
        self.end_time = datetime.now(timezone.utc)
        if self.start_time:
            time_diff = self.end_time - self.start_time
            self.time_taken_minutes = round(time_diff.total_seconds() / 60, 2)
        self.calculate_score()


class StudentProgress(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "student_progress"

    student_id = UnicodeAttribute()
    lesson_id = UnicodeAttribute()
    completion_status = UnicodeAttribute(default="not_started")  # not_started, in_progress, completed
    proficiency_level = NumberAttribute(default=0)  # 0-100 scale
    knowledge_gaps = JSONAttribute(null=True)  # Structured data for learning analytics
    last_accessed = UTCDateTimeAttribute(default_for_new=lambda: datetime.now(timezone.utc))
    interaction_count = NumberAttribute(default=0)
    time_spent_minutes = NumberAttribute(default=0)
    quiz_attempts = NumberAttribute(default=0)
    best_quiz_score = NumberAttribute(null=True)

    # GSI for querying progress by lesson
    lesson_index = StudentProgressLessonIndex()

    def update_progress(self, time_spent: int = 0, interaction: bool = True):
        """Update progress metrics"""
        if time_spent > 0:
            self.time_spent_minutes += time_spent
        if interaction:
            self.interaction_count += 1
        self.last_accessed = datetime.now(timezone.utc)

    def mark_completed(self):
        """Mark lesson as completed"""
        self.completion_status = "completed"
        self.last_accessed = datetime.now(timezone.utc)


# --- Additional Models for Enhanced Functionality ---


class Notification(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "notifications"

    user_id = UnicodeAttribute()
    title = UnicodeAttribute()
    message = UnicodeAttribute()
    notification_type = UnicodeAttribute()  # info, warning, success, error
    is_read = BooleanAttribute(default=False)
    action_url = UnicodeAttribute(null=True)
    expires_at = UTCDateTimeAttribute(null=True)


class LessonRating(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "lesson_ratings"

    lesson_id = UnicodeAttribute()
    student_id = UnicodeAttribute()
    rating = NumberAttribute()  # 1-5 scale
    review = UnicodeAttribute(null=True)
    is_anonymous = BooleanAttribute(default=False)


class StudySession(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "study_sessions"

    student_id = UnicodeAttribute()
    lesson_id = UnicodeAttribute(null=True)
    subject_id = UnicodeAttribute(null=True)
    session_start = UTCDateTimeAttribute(default_for_new=lambda: datetime.now(timezone.utc))
    session_end = UTCDateTimeAttribute(null=True)
    activities_completed = NumberAttribute(default=0)
    focus_score = NumberAttribute(null=True)  # 1-100 based on interaction patterns