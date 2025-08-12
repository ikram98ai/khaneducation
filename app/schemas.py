from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict
from .models import UserRoleEnum, LessonStatusEnum, DifficultyLevelEnum, LanguageChoicesEnum


class SubjectBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    grade_level: int = Field(..., ge=1, le=12)


class SubjectCreate(SubjectBase):
    pass


class Subject(SubjectBase):
    id: str
    total_lessons: Optional[int] = None
    completed_lessons: Optional[int] = None
    progress: Optional[float] = 0.0

    class Config:
        from_attributes = True


class SubjectDetail(Subject):
    lessons: List["Lesson"] = []


class LessonBase(BaseModel):
    title: str = Field(..., max_length=255)
    language: str
    content: Optional[str] = None


class LessonCreate(LessonBase):
    subject_id: Optional[str] = None
    instructor_id: Optional[str] = None
    status: Optional[LessonStatusEnum] = None


class Lesson(LessonBase):
    id: str
    instructor_id: str
    subject_id: Optional[str] = None
    status: LessonStatusEnum
    created_at: datetime
    order_in_subject: Optional[int] = None
    verified_at: Optional[datetime] = None
    progress: Optional[float] = 0.0

    class Config:
        from_attributes = True


class PracticeTaskBase(BaseModel):
    lesson_id: str
    content: str
    solution: str
    difficulty: DifficultyLevelEnum = DifficultyLevelEnum.MEDIUM


class PracticeTask(PracticeTaskBase):
    id: str
    ai_generated: bool
    created_at: datetime

    class Config:
        from_attributes = True


class QuizBase(BaseModel):
    lesson_id: str
    quiz_version: int = 1


class QuizQuestion(BaseModel):
    question_id: str
    question_text: str
    question_type: str
    options: List[str] = []
    correct_answer: Optional[str] = None


class Quiz(QuizBase):
    id: str
    created_at: datetime
    lesson_title: Optional[str] = None
    quiz_questions: List[QuizQuestion] = []

    class Config:
        from_attributes = True


class QuizAttemptBase(BaseModel):
    student_id: str
    lesson_id: str


class QuizResponse(BaseModel):
    question_id: str
    student_answer: str
    is_correct: Optional[bool] = None


class QuizAttempt(QuizAttemptBase):
    id: str
    lesson_title: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    score: Optional[float] = None
    passed: bool
    ai_feedback: Optional[str] = None
    quiz_version: Optional[int] = None
    cheating_detected: bool
    responses: List[QuizResponse] = []

    class Config:
        from_attributes = True


class QuizSubmissionResponse(BaseModel):
    attempt: QuizAttempt
    ai_feedback: str


class DashboardStats(BaseModel):
    completed_lessons: int
    total_lessons: int
    avg_score: float
    streak: int


class AIContentRequest(BaseModel):
    user_messages: List[Dict[str, str]]
    subject_id: str
    lesson_id: Optional[str] = None


class StudentResponseBase(BaseModel):
    attempt_id: str
    question_id: str
    student_answer: str
    is_correct: bool


class StudentResponse(StudentResponseBase):
    id: str

    class Config:
        from_attributes = True


class StudentDashboard(BaseModel):
    enrollments: List[Subject]
    stats: DashboardStats

    class Config:
        from_attributes = True


class StudentBase(BaseModel):
    language: LanguageChoicesEnum
    current_grade: int = Field(..., ge=1, le=12)


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    language: Optional[LanguageChoicesEnum] = None
    current_grade: Optional[int] = Field(None, ge=1, le=12)


class Student(StudentBase):
    user_id: str

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRoleEnum] = UserRoleEnum.STUDENT
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class User(UserBase):
    id: str

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
    user_id: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRoleEnum] = None


class AdminDashboard(BaseModel):
    total_students: int
    total_lessons: int
    total_subjects: int
    total_quizzes: int
    recent_lessons: List[Lesson]

    class Config:
        from_attributes = True


class QuizAttemptResponsesOut(BaseModel):
    question_id: str
    question_text: str
    question_type: str
    student_answer: str
    correct_answer: str


class QuizAttemptOut(BaseModel):
    id: str
    lesson_title: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    score: Optional[float] = None
    passed: bool
    ai_feedback: Optional[str] = None
    quiz_version: Optional[int] = None
    cheating_detected: bool
    responses: List[QuizAttemptResponsesOut] = []

    class Config:
        from_attributes = True
