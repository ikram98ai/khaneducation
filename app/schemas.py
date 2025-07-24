from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

from .models import UserRole, LanguageChoices, LessonStatus, DifficultyLevel


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


class SubjectDetail(Subject):
    lessons: List["Lesson"] = []


class LessonBase(BaseModel):
    title: str = Field(..., max_length=255)
    content:Optional[str] = None


class LessonCreate(LessonBase):
    subject_id: Optional[int] = None
    instructor_id: Optional[int] = None
    status: Optional[LessonStatus] = None


class Lesson(LessonBase):
    id: int
    instructor_id: int
    subject_id: Optional[int] = None
    status: LessonStatus
    created_at: datetime
    verified_at: Optional[datetime] = None
    progress: Optional[float] = 0.0

    class Config:
        from_attributes = True


class EnrollmentBase(BaseModel):
    student_id: int
    subject_id: int


class EnrolledSubject(Subject):
    enrolled_at: datetime
    total_lessons: Optional[int] = None
    completed_lessons: Optional[int] = None
    progress: Optional[float] = None

    class Config:
        from_attributes = True


class Enrollment(EnrollmentBase):
    id: int
    enrolled_at: datetime

    class Config:
        from_attributes = True


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
    quiz_id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
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
    lesson_title: str
    start_time: datetime
    end_time: Optional[datetime] = None
    score: Optional[float] = None
    passed: bool
    quiz_version:int
    cheating_detected: bool

    class Config:
        from_attributes = True


class QuizResponse(BaseModel):
    question_id:int
    answer: str

class QuizSubmission(BaseModel):
    quiz_id: int
    responses: List[QuizResponse]

class QuizSubmissionResponse(BaseModel):
    attempt: QuizAttempt
    ai_feedback: str
    regenerated_quiz: Optional[Quiz] = None

class DashboardStats(BaseModel):
    completedLessons: int
    totalLessons: int
    avgScore: float
    streak: int


class AIContentRequest(BaseModel):
    message: str
    context: Optional[str] = None


class StudentResponseBase(BaseModel):
    attempt_id: int
    question_id: int
    student_answer: str
    is_correct: bool


class StudentResponse(StudentResponseBase):
    id: int

    class Config:
        from_attributes = True


class StudentDashboard(BaseModel):
    enrollments: List["EnrolledSubject"]
    recent_attempts: List["QuizAttempt"]

    class Config:
        from_attributes = True


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
