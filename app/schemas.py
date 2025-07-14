from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional


from .models import UserRole, LanguageChoices


class SubjectBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    grade_level: int = Field(..., ge=1, le=12)
    language: LanguageChoices = LanguageChoices.EN


class SubjectCreate(SubjectBase):
    pass


class Subject(SubjectBase):
    id: int
    total_lessons: Optional[int] = None
    completed_lessons: Optional[int] = None
    progress: Optional[float] = None

    class Config:
        from_attributes = True


class LessonStatus(str, Enum):
    DRAFT = "DR"
    VERIFIED = "VE"


class LessonBase(BaseModel):
    title: str = Field(..., max_length=255)
    content: str


class LessonCreate(LessonBase):
    subject_id: Optional[int] = None
    instructor_id: Optional[int] = None


class Lesson(LessonBase):
    id: int
    instructor_id: int
    status: LessonStatus
    created_at: datetime
    verified_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EnrollmentBase(BaseModel):
    student_id: int
    subject_id: int


class Enrollment(EnrollmentBase):
    id: int
    enrolled_at: datetime

    class Config:
        from_attributes = True


class DifficultyLevel(str, Enum):
    EASY = "EA"
    MEDIUM = "ME"
    HARD = "HA"


class PracticeTaskBase(BaseModel):
    lesson_id: int
    content: str
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM


class PracticeTask(PracticeTaskBase):
    id: int
    ai_generated: bool
    created_at: datetime

    class Config:
        from_attributes = True


class QuizQuestionBase(BaseModel):
    question_text: str
    correct_answer: str


class QuizQuestion(QuizQuestionBase):
    id: int

    class Config:
        from_attributes = True


class QuizBase(BaseModel):
    lesson_id: int
    version: int = 1


class Quiz(QuizBase):
    id: int
    ai_generated: bool
    created_at: datetime
    questions: List[QuizQuestion] = []

    class Config:
        from_attributes = True


class QuizAttemptBase(BaseModel):
    quiz_id: int
    student_id: int


class QuizAttempt(QuizAttemptBase):
    id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    score: Optional[float] = None
    passed: bool
    cheating_detected: bool

    class Config:
        from_attributes = True


class StudentResponseBase(BaseModel):
    question_id: int
    student_answer: str
    is_correct: bool


class StudentResponse(StudentResponseBase):
    id: int

    class Config:
        from_attributes = True


class QuizSubmission(BaseModel):
    quiz_id: int
    responses: List[dict]


class StudentDashboard(BaseModel):
    student: "Student"
    enrollments: List["Enrollment"]
    recent_attempts: List["QuizAttempt"]
    practice_tasks: List["PracticeTask"]

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    completedLessons: int
    totalLessons: int
    avgScore: float
    streak: int


class AIContentRequest(BaseModel):
    message: str
    context: Optional[str] = None


class StudentBase(BaseModel):
    language: LanguageChoices
    current_grade: int = Field(..., ge=1, le=12)


class StudentCreate(StudentBase):
    pass


class Student(StudentBase):
    user_id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        from_attributes = True


class StudentProfile(BaseModel):
    user: User
    student_profile: Optional[Student] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None


class AdminDashboard(BaseModel):
    total_students: int
    total_lessons: int
    total_subjects: int
    total_quizzes: int
    recent_lessons: List[Lesson]
    recent_attempts: List[QuizAttempt]

    class Config:
        from_attributes = True
