ASSISTANT_PROMPT = """You are a helpful AI assistant in {language} language. Use the provided context to answer the user's query.
Context: {context}
"""

LESSON_GENERATOR_PROMPT = """You are an expert instructor of {subject}. Generate a comprehensive lesson about '{title}' for grade {grade_level} students in {language}.
The lesson should include an introduction, learning objectives, a full and detailed main content, a summary, and additional resources.
"""

PRACTICE_TASK_GENERATOR_PROMPT = """Based on the given lesson content, generate a list of 5 practice tasks for grade {grade_level} students in {language} with step by step solution.

Each task should be in the format:
{{
    "content": "...",
    "difficulty": 'EA', 'ME' or 'HA',
    "solution": "...",
}}
"""

QUIZ_GENERATOR_PROMPT = """Based on the given lesson content, generate a quiz with 5 questions for grade {grade_level} students in {language}.

Each question should be in the format:
{{
    "question_text": "...",
    "options": ["...", "...", "...", "..."],
    "question_type": "MCQs",
    "correct_answer": "..."
}}
"""

QUIZ_FEEDBACK_GENERATOR_PROMPT = """Provide step-by-step three liner feedback for the student's quiz answers according to the following correct answers.
Correct Answers: {correct_answers}
"""
