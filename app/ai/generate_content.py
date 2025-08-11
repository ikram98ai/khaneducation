"""
AI functions for generating educational content.
"""

from pydantic import BaseModel
from typing import Literal
from .prompts import (
    ASSISTANT_PROMPT,
    LESSON_GENERATOR_PROMPT,
    PRACTICE_TASK_GENERATOR_PROMPT,
    QUIZ_GENERATOR_PROMPT,
    QUIZ_FEEDBACK_GENERATOR_PROMPT,
)
from .utils import get_completion


async def ai_assistant(user_messages, context, language):
    """
    AI assistant to answer user queries with context.
    """
    result = await get_completion(ASSISTANT_PROMPT.format(context=context, language=language), user_messages=user_messages)
    return result


async def generate_lesson(subject, title, grade_level, language):
    """
    Generate lesson content using AI based on title, grade level, and language.
    """
    result = await get_completion(
        LESSON_GENERATOR_PROMPT.format(subject=subject, title=title, grade_level=grade_level, language=language),
        f"Generate lesson '{title}' for {subject}",
    )
    return result


class PracticeTask(BaseModel):
    content: str
    difficulty: Literal["easy", "medium", "hard"]
    solution: str


class PracticeTasks(BaseModel):
    tasks: list[PracticeTask]


async def generate_practice_tasks(lesson_content, grade_level, language):
    """
    Generate practice tasks based on lesson content.
    """

    result = await get_completion(
        PRACTICE_TASK_GENERATOR_PROMPT.format(grade_level=grade_level, language=language),
        f"Generate practice tasks from the following lesson content:\n\n:Lesson Content: {lesson_content}",
        output_type=PracticeTasks,
    )

    tasks = result.tasks
    return tasks


class QuizQuestion(BaseModel):
    question_text: str
    options: list[str]
    question_type: str
    correct_answer: str


class Quiz(BaseModel):
    questions: list[QuizQuestion]


async def generate_quiz_questions(lesson_content, grade_level, language):
    """
    Generate quiz questions based on lesson content.
    """
    result = await get_completion(
        QUIZ_GENERATOR_PROMPT.format(grade_level=grade_level, language=language),
        f"Generate Quiz questions from the following lesson content:\n\n:Lesson Content: {lesson_content}",
        output_type=Quiz,
    )
    return result.questions


async def generate_quiz_feedback(student_answers, correct_answers):
    """
    Generate personalized feedback for quiz attempts.
    """
    result = await get_completion(QUIZ_FEEDBACK_GENERATOR_PROMPT.format(correct_answers=correct_answers), f"Student's Answers: {student_answers}")
    return result
