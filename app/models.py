from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    Boolean,
    Float,
    Enum,
    CheckConstraint,
)
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.ext.hybrid import hybrid_property
from .database import Base
import enum


class UserRole(enum.Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    CONTENT_MANAGER = "content_manager"
    STAFF = "staff"
    ADMIN = "admin"


class LanguageChoices(enum.Enum):
    EN = "English"
    FR = "French"
    PS = "Pashto"
    ES = "Spanish"
    AR = "Arabic"
    FA = "Persian"
    UR = "Urdu"


class LessonStatus(enum.Enum):
    DRAFT = "DR"
    VERIFIED = "VE"


class DifficultyLevel(enum.Enum):
    EASY = "EA"
    MEDIUM = "ME"
    HARD = "HA"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, unique=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


class Subject(Base):
    __tablename__ = "subjects"
    __table_args__ = (CheckConstraint("grade_level BETWEEN 1 AND 12", name="grade_level_range"),)

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    grade_level = Column(Integer, nullable=False)
    language = Column(Enum(LanguageChoices, values_callable=lambda x: [e.value for e in x]), default=LanguageChoices.EN)

    lessons = relationship("Lesson", back_populates="subject")
    enrollments = relationship("Enrollment", back_populates="subject")

    @validates("name")
    def normalize_name(self, key, name):
        return name.strip().title()


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(Enum(LessonStatus), default=LessonStatus.DRAFT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_at = Column(DateTime(timezone=True), nullable=True)

    subject = relationship("Subject", back_populates="lessons")
    practice_tasks = relationship("PracticeTask", back_populates="lesson")
    quizzes = relationship("Quiz", back_populates="lesson")


class Student(Base):
    __tablename__ = "students"
    __table_args__ = (CheckConstraint("current_grade BETWEEN 1 AND 12", name="student_grade_range"),)

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    language = Column(Enum(LanguageChoices), default=LanguageChoices.EN)
    current_grade = Column(Integer, nullable=False)

    enrollments = relationship("Enrollment", back_populates="student")
    quiz_attempts = relationship("QuizAttempt", back_populates="student")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.user_id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="enrollments")
    subject = relationship("Subject", back_populates="enrollments")


class PracticeTask(Base):
    __tablename__ = "practice_tasks"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    content = Column(Text, nullable=False)
    difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.MEDIUM)
    ai_generated = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    lesson = relationship("Lesson", back_populates="practice_tasks")


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    version = Column(Integer, default=1)
    ai_generated = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    lesson = relationship("Lesson", back_populates="quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz")
    attempts = relationship("QuizAttempt", back_populates="quiz")


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    option_a = Column(String, nullable=False)
    option_b = Column(String, nullable=False)
    option_c = Column(String, nullable=False)
    option_d = Column(String, nullable=False)
    correct_answer = Column(String, nullable=False)

    quiz = relationship("Quiz", back_populates="questions")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    __table_args__ = (CheckConstraint("score BETWEEN 0 AND 100", name="score_range"),)

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.user_id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    score = Column(Float, nullable=True)
    passed = Column(Boolean, default=False)
    cheating_detected = Column(Boolean, default=False)

    student = relationship("Student", back_populates="quiz_attempts")
    quiz = relationship("Quiz", back_populates="attempts")
    responses = relationship("StudentResponse", back_populates="attempt")

    @hybrid_property
    def lesson_title(self):
        return self.quiz.lesson.title if self.quiz and self.quiz.lesson else None

    @hybrid_property
    def quiz_version(self):
        return self.quiz.version if self.quiz else None


class StudentResponse(Base):
    __tablename__ = "student_responses"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("quiz_attempts.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("quiz_questions.id"), nullable=False)
    student_answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False)

    attempt = relationship("QuizAttempt", back_populates="responses")
    question = relationship("QuizQuestion")
