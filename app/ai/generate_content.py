"""
AI functions for generating educational content.
"""
from agents import Agent, Runner
from pydantic import BaseModel
from .prompts import (
    ASSISTANT_PROMPT,
    LESSON_GENERATOR_PROMPT,
    PRACTICE_TASK_GENERATOR_PROMPT,
    QUIZ_GENERATOR_PROMPT,
    QUIZ_FEEDBACK_GENERATOR_PROMPT,
)
from .utils import get_model

model = get_model()


async def ai_assistant(query_text, context):
    """
    AI assistant to answer user queries with context.
    """
    agent = Agent(
        name="AI Assistant",
        instructions=ASSISTANT_PROMPT.format(
            context=context, query_text=query_text
        ),
        model=model,
    )
    result = await Runner.run(agent, input="")
    return result.final_output


async def generate_lesson(title, grade_level, language):
    """
    Generate lesson content using AI based on title, grade level, and language.
    """
    agent = Agent(
        name="Lesson Generator",
        instructions=LESSON_GENERATOR_PROMPT.format(
            title=title, grade_level=grade_level, language=language
        ),
        model=model,
    )
    result = await Runner.run(agent, input="")
    return result.final_output


class PracticeTask(BaseModel):
    content: str
    difficulty: str
    solution: str


class PracticeTasks(BaseModel):
    tasks: list[PracticeTask]


async def generate_practice_tasks(lesson_content, grade_level, language):
    """
    Generate practice tasks based on lesson content.
    """
    agent = Agent(
        name="Practice Task Generator",
        instructions=PRACTICE_TASK_GENERATOR_PROMPT.format(
            lesson_content=lesson_content,
            grade_level=grade_level,
            language=language,
        ),
        model=model,
        output_type=PracticeTasks,
    )
    result = await Runner.run(agent, input="")
    # The output is a list of tasks, so we need to parse it
    tasks = result.final_output.tasks
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
    agent = Agent(
        name="Quiz Generator",
        instructions=QUIZ_GENERATOR_PROMPT.format(
            lesson_content=lesson_content,
            grade_level=grade_level,
            language=language,
        ),
        model=model,
        output_type=Quiz,
    )
    result = await Runner.run(agent, input="")
    # The output should be a JSON object with a list of questions
    return result.final_output.questions


async def generate_quiz_feedback(student_answers, correct_answers):
    """
    Generate personalized feedback for quiz attempts.
    """
    agent = Agent(
        name="Quiz Feedback Generator",
        instructions=QUIZ_FEEDBACK_GENERATOR_PROMPT.format(
            student_answers=student_answers, correct_answers=correct_answers
        ),
        model=model,
    )
    result = await Runner.run(agent, input="")
    return result.final_output