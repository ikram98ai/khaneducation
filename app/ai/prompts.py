ASSISTANT_PROMPT = """You are a helpful AI assistant. Use the provided context to answer the user's query.
Context: {context}
Query: {query_text}
"""

LESSON_GENERATOR_PROMPT = """You are an expert instructor of {subject}. Generate a comprehensive lesson about '{title}' for grade {grade_level} students in {language}.
The lesson should include an introduction, learning objectives, main content, a summary, and additional resources.
"""

PRACTICE_TASK_GENERATOR_PROMPT = """Based on the following lesson content, generate a list of 5 practice tasks for grade {grade_level} students in {language}.
Lesson Content: {lesson_content}

Each task should be in the format:
{{
    "content": "...",
    "difficulty": "...",
    "solution": "...",
}}
"""

QUIZ_GENERATOR_PROMPT = """Based on the following lesson content, generate a quiz with 5 questions for grade {grade_level} students in {language}.
Each question should be in the format:
{{
    "question_text": "...",
    "options": ["...", "...", "...", "..."],
    "question_type": "MCQs",
    "correct_answer": "..."
}}
Lesson Content: {lesson_content}
"""

QUIZ_FEEDBACK_GENERATOR_PROMPT = """Provide step-by-step feedback for the following quiz answers.
Student Answers: {student_answers}
Correct Answers: {correct_answers}
"""