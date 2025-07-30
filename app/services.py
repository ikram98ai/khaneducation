# app/services.py
# Remove: from sqlalchemy.orm import Session
# Remove: from sqlalchemy.sql import func
# Remove: from datetime import datetime, timedelta (Keep if used for non-DB logic)
from typing import List
# Remove: from . import models, schemas, crud (models and crud will be replaced)
from . import schemas # Keep schemas
# Remove: from .crud import crud_lesson, crud_practice_task, crud_quiz, crud_quiz_question, crud_quiz_attempt, crud_student_response
from .ai import generate_content as ai

# --- PynamoDB Imports ---
from .models import Lesson, PracticeTask, Quiz, QuizQuestion, QuizAttempt, StudentResponse
from datetime import datetime, timezone # Use timezone-aware datetime for DynamoDB
import uuid # If using UUIDs or need unique IDs

def create_lesson_with_content(subject_id: int, instructor_id: int, title: str) -> Lesson: # Return PynamoDB model
    # --- Fetch Subject (Adapt based on how you pass/get subject) ---
    # This part depends on how the subject is validated upstream.
    # For now, assume it exists or handle error upstream.
    # --- End Fetch Subject ---

    try:
        # --- Fetch Subject Details (if needed for AI) ---
        # This might be passed in or fetched here. Example fetch:
        # from .models_pynamodb import Subject
        # try:
        #     subject = Subject.get(subject_id)
        # except Subject.DoesNotExist:
        #     raise ValueError("Subject not found")
        # grade_level = subject.grade_level
        # language_value = subject.language # This is the string value
        # --- End Fetch Subject Details ---

        # Placeholder: Get grade_level and language_value from context or upstream
        # This logic needs to be clarified how subject details are obtained.
        # For demonstration, using dummy values or assuming they are passed.
        # Let's assume grade_level and language_value are obtained somehow.
        # You might need to pass subject object or details into this function.

        # Example placeholder values (replace with actual logic to get these)
        grade_level = 5 # Example
        language_value = "English" # Example, use subject.language if subject object is available

        lesson_content = ai.generate_lesson(
            title=title,
            grade_level=grade_level,
            language=language_value,
        )
        # Create Lesson instance (PynamoDB)
        # Assuming Lesson PK is subject_id (hash) + new unique id (range)
        # You might generate a unique lesson ID or let DynamoDB/Pynamo handle it if using UUIDs
        new_lesson_id = int(uuid.uuid4()) # Example ID generation, adapt as needed
        db_lesson = Lesson(
            subject_id=subject_id, # hash key
            id=new_lesson_id,      # range key
            instructor_id=instructor_id,
            title=title,
            content=lesson_content,
            status="DR", # Use string value for enum
            created_at=datetime.now(timezone.utc)
        )
        db_lesson.save() # Save to DynamoDB


        # Create practice task
        task_content = ai.generate_practice_task(
            lesson_content=lesson_content,
            difficulty="ME",
            grade_level=grade_level,
            language=language_value,
        )
        # Assuming PracticeTask PK is a unique ID
        new_task_id = int(uuid.uuid4())
        practice_task = PracticeTask(
            id=new_task_id,
            lesson_id=new_lesson_id, # Link to lesson
            content=task_content,
            difficulty="ME", # Use string value
            ai_generated=True,
            created_at=datetime.now(timezone.utc)
        )
        practice_task.save()

        # Create quiz
        quiz_data = ai.generate_quiz(
            lesson_content=lesson_content,
            grade_level=grade_level,
            language=language_value,
        )
        # Assuming Quiz PK is a unique ID
        new_quiz_id = int(uuid.uuid4())
        db_quiz = Quiz(
            id=new_quiz_id,
            lesson_id=new_lesson_id, # Link to lesson
            version=1,
            ai_generated=True,
            created_at=datetime.now(timezone.utc)
        )
        db_quiz.save()

        # Create quiz questions
        for question_data in quiz_data["questions"]:
            new_question_id = int(uuid.uuid4())
            quiz_question = QuizQuestion(
                id=new_question_id,
                quiz_id=new_quiz_id, # Link to quiz
                question_text=question_data["question"],
                option_a=question_data["option_a"],
                option_b=question_data["option_b"],
                option_c=question_data["option_c"],
                option_d=question_data["option_d"],
                correct_answer=question_data["correct_answer"]
            )
            quiz_question.save()

        # Refresh lesson object if needed (PynamoDB objects are usually up-to-date after save)
        # Or re-fetch if necessary. PynamoDB doesn't have a direct refresh like SQLAlchemy.
        # db_lesson = Lesson.get(subject_id, new_lesson_id) # Re-fetch example

        return db_lesson # Return the PynamoDB model instance

    except Exception as e: # Catch specific PynamoDB exceptions if needed (e.g., PutError)
        # Handle rollback/compensation logic if partial creation occurred (DynamoDB is not transactional like SQL)
        # This is more complex in DynamoDB. Consider using DynamoDB Transactions for critical multi-item writes.
        print(f"Error in create_lesson_with_content: {e}") # Use logging in production
        raise # Re-raise or raise a custom service exception


def submit_quiz_responses(quiz_id: int, student_id: int, responses: List[schemas.QuizResponse]) -> schemas.QuizSubmissionResponse:
    try:
        # Fetch quiz
        # Assuming Quiz PK is id
        try:
            quiz = Quiz.get(quiz_id)
        except Quiz.DoesNotExist:
            raise ValueError("Quiz not found")

        # Create quiz attempt
        # Assuming QuizAttempt PK is student_id (hash) + new unique id (range)
        new_attempt_id = int(uuid.uuid4())
        db_attempt = QuizAttempt(
            student_id=student_id, # hash key
            id=new_attempt_id,     # range key
            quiz_id=quiz_id,       # Link to quiz
            start_time=datetime.now(timezone.utc),
            # end_time, score, passed will be set later
            passed=False,
            cheating_detected=False
        )
        db_attempt.save() # Save initial attempt

        correct_count = 0
        student_answers = []
        correct_answers = []

        # Process responses
        for response in responses:
            question_id = response.question_id
            answer = response.answer
            # Fetch question
            try:
                question = QuizQuestion.get(question_id)
            except QuizQuestion.DoesNotExist:
                continue # Or handle error

            is_correct = answer.strip().lower() == question.correct_answer.strip().lower()
            if is_correct:
                correct_count += 1
            student_answers.append(answer)
            correct_answers.append(question.correct_answer)

            # Create response record
            # Assuming StudentResponse PK is a unique ID
            new_response_id = int(uuid.uuid4())
            student_response = StudentResponse(
                id=new_response_id,
                attempt_id=new_attempt_id, # Link to attempt
                question_id=question_id,   # Link to question
                student_answer=answer,
                is_correct=is_correct
            )
            student_response.save()

        # Calculate score
        total_questions = len(responses)
        score = (correct_count / total_questions) * 100 if total_questions > 0 else 0

        # Update attempt
        db_attempt.score = score
        db_attempt.passed = score >= 70
        db_attempt.end_time = datetime.now(timezone.utc)
        db_attempt.save() # Update the attempt record

        # Generate AI feedback (no DB interaction here)
        ai_feedback = ai.generate_quiz_feedback(student_answers=student_answers, correct_answers=correct_answers)

        # Regenerate quiz if needed
        regenerated_quiz = None
        if score < 60 and quiz.ai_generated:
            # Fetch lesson details (assuming quiz has lesson_id)
            try:
                lesson = Lesson.get(quiz.lesson_id) # Simplified, might need subject_id too
                # Find max version for this lesson (requires a query)
                # This is complex in DynamoDB without a GSI on lesson_id for Quiz
                # Assume a function or logic exists to find max version
                # Placeholder logic:
                # quizzes_for_lesson = list(Quiz.query(lesson.subject_id, filter_condition=Quiz.lesson_id == lesson.id)) # If GSI or appropriate key
                # For now, assume we can query or fetch related quizzes somehow
                # Or pass lesson object which might have quizzes if modeled differently
                # Let's assume we can get the lesson and then find quizzes for it
                # This part needs careful design of your DynamoDB access patterns

                # Placeholder for finding max version (inefficient without GSI/index)
                # A better approach is to have a GSI on Quiz table with lesson_id as hash key
                # max_version = 1 # Simplified
                # Or query based on access pattern design

                # Example assuming access pattern allows querying quizzes by lesson_id efficiently
                # This depends on your GSI design. If not, you might need to scan or re-think.
                # For demonstration, let's assume we can get related quizzes or max version.
                # You'll need to adapt this based on your actual data access strategy.

                 # Placeholder: Assume we can determine new version
                new_version = 2 # Example, replace with actual logic

                new_quiz_data = ai.generate_quiz(
                    lesson_content=lesson.content,
                    grade_level=5, # Placeholder, get from lesson.subject.grade_level
                    language="English" # Placeholder, get from lesson.subject.language
                )
                 # Create new quiz
                new_quiz_id_2 = int(uuid.uuid4())
                new_quiz = Quiz(
                    id=new_quiz_id_2,
                    lesson_id=lesson.id,
                    version=new_version,
                    ai_generated=True,
                    created_at=datetime.now(timezone.utc)
                )
                new_quiz.save()

                # Create new questions
                for question_data in new_quiz_data["questions"]:
                    new_question_id_2 = int(uuid.uuid4())
                    new_question = QuizQuestion(
                        id=new_question_id_2,
                        quiz_id=new_quiz_id_2,
                        question_text=question_data["question"],
                        option_a=question_data["option_a"],
                        option_b=question_data["option_b"],
                        option_c=question_data["option_c"],
                        option_d=question_data["option_d"],
                        correct_answer=question_data["correct_answer"]
                    )
                    new_question.save()

                regenerated_quiz = new_quiz # Assign PynamoDB model

            except Lesson.DoesNotExist:
                 print("Lesson not found for quiz during regeneration") # Log appropriately
                 # Handle if lesson not found, maybe don't regenerate
                 regenerated_quiz = None
            except Exception as e:
                 print(f"Error during quiz regeneration: {e}") # Log appropriately
                 regenerated_quiz = None # Don't fail the whole submission


        # Return data (adapt if returning PynamoDB models directly or converting)
        # The schema expects certain fields. Ensure the data matches.
        # You might need to construct the QuizAttempt schema-compliant object
        # or fetch the final attempt data.

        # Example of constructing response data
        attempt_schema_data = schemas.QuizAttempt(
             id=db_attempt.id,
             quiz_id=db_attempt.quiz_id,
             student_id=db_attempt.student_id,
             start_time=db_attempt.start_time,
             end_time=db_attempt.end_time,
             score=db_attempt.score,
             passed=db_attempt.passed,
             quiz_version=quiz.version_number, # Get from original quiz
             cheating_detected=db_attempt.cheating_detected,
             lesson_title="Placeholder" # Need to fetch lesson title, complex in DynamoDB
             # You might store lesson_title denormalized in QuizAttempt during creation
             # or fetch it here via a separate query.
        )

        return schemas.QuizSubmissionResponse(
            attempt=attempt_schema_data, # Pass the schema object
            ai_feedback=ai_feedback,
            regenerated_quiz=regenerated_quiz # This should ideally be a schema object too, convert if needed
        )

    except Exception as e: # Catch PynamoDB exceptions, value errors, etc.
        print(f"Error in submit_quiz_responses: {e}") # Use logging
        raise # Re-raise or custom exception

# --- get_student_dashboard_stats needs significant rewrite ---
# Calculating counts, averages, and complex queries like streaks are much harder in DynamoDB
# without careful design of access patterns and potentially GSIs/LSIs.
# This is a simplified example highlighting the challenges.

# Example: Requires GSI on QuizAttempt by student_id, date, passed
# Example: Requires GSI on Lesson by subject_id
# Example: Requires GSI on QuizAttempt by student_id for average score
# Example: Requires complex logic for streaks (might need to store/retrieve last attempt dates)

# Placeholder/Demonstration (Not efficient, needs DynamoDB design):
def get_student_dashboard_stats(student_id: int) -> schemas.DashboardStats:
    # --- Completed Lessons (Very Complex in DynamoDB) ---
    # Need: Lessons where student passed a quiz for that lesson.
    # Requires: Joining data or pre-calculating.
    # Approach 1: Query QuizAttempt by student_id where passed=True.
    #            For each attempt, get quiz_id, then get lesson_id.
    #            Get distinct lesson_ids.
    #            Count them.
    #            This requires multiple round trips or a GSI on QuizAttempt.quiz_id
    #            and potentially storing lesson_id in QuizAttempt for easier lookup.
    #            Or denormalizing lesson info into QuizAttempt.
    completed_lessons = 0 # Placeholder

    # --- Total Lessons (Complex) ---
    # Need: Total lessons in subjects the student is enrolled in.
    # Requires: Get student's enrollments (need Enrollment model and GSI?).
    #           For each enrollment, get subject_id.
    #           Count lessons for each subject_id (need GSI on Lesson.subject_id).
    total_lessons = 0 # Placeholder

    # --- Average Score (Moderate with GSI) ---
    # Need: Average of QuizAttempt.score for a student.
    # Requires: GSI on QuizAttempt with student_id as hash key.
    #           Query all attempts for student, sum scores, count, calculate average.
    avg_score = 0.0 # Placeholder

    # --- Streak (Very Complex) ---
    # Need: Consecutive days student passed a quiz.
    # Requires: GSI on QuizAttempt with student_id as hash key and date as sort key (or composite).
    #           Query attempts for student, ordered by date/time.
    #           Check if end_time dates are consecutive and passed=True.
    #           This is a non-trivial query pattern in DynamoDB.
    streak = 0 # Placeholder

    # --- Actual Implementation (Requires careful DynamoDB design) ---
    # This is a significant part of the migration challenge.
    # You'll need to design your tables and indexes to support these queries efficiently.
    # Consider:
    # 1. Denormalizing data (e.g., storing lesson_id in QuizAttempt).
    # 2. Creating GSIs for common query patterns (student_id, subject_id, date).
    # 3. Using DynamoDB Streams and Lambda to maintain aggregate data (e.g., user stats).
    # 4. Accepting that some queries might be slower or require multiple requests.

    # Example placeholder logic (NOT EFFICIENT, for illustration):
    # from .models_pynamodb import Enrollment, QuizAttempt
    # completed_lessons_set = set()
    # try:
    #     # Get enrollments for student (need GSI or appropriate key structure)
    #     # enrollments = list(Enrollment.query(...)) # Adapt based on key design
    #     # subject_ids = [e.subject_id for e in enrollments]
    #     # Get passed quiz attempts for student
    #     passed_attempts = list(QuizAttempt.student_id_index.query(student_id, filter_condition=QuizAttempt.passed == True)) # Hypothetical GSI
    #     for attempt in passed_attempts:
    #         try:
    #             quiz = Quiz.get(attempt.quiz_id)
    #             completed_lessons_set.add(quiz.lesson_id) # Need lesson_id in Quiz or attempt
    #         except Quiz.DoesNotExist:
    #             pass
    #     completed_lessons = len