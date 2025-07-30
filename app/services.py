# app/services.py
from typing import List
from . import schemas  # Keep schemas
from .ai import generate_content as ai
from .models import Lesson, PracticeTask, Quiz, Subject, QuizAttempt, Student
from pynamodb.transactions import TransactWrite
from datetime import datetime, timezone  # Use timezone-aware datetime for DynamoDB
import uuid  # If using UUIDs or need unique IDs


def create_lesson_with_content(subject_id: int, instructor_id: int, title: str) -> Lesson:  # Return PynamoDB model
    try:
        try:
            subject = Subject.get(subject_id)
        except Subject.DoesNotExist:
            raise ValueError("Subject not found")
        grade_level = subject.grade_level
        language_value = subject.language

        lesson_content = ai.generate_lesson(
            title=title,
            grade_level=grade_level,
            language=language_value,
        )

        new_lesson_id = int(uuid.uuid4())
        db_lesson = Lesson(
            subject_id=subject_id,
            id=new_lesson_id,
            instructor_id=instructor_id,
            title=title,
            content=lesson_content,
            status="DR",
            created_at=datetime.now(timezone.utc),
        )

        # Practice Task
        task_content = ai.generate_practice_task(
            lesson_content=lesson_content,
            difficulty="ME",
            grade_level=grade_level,
            language=language_value,
        )

        new_task_id = int(uuid.uuid4())
        practice_task = PracticeTask(
            id=new_task_id, lesson_id=new_lesson_id, content=task_content, difficulty="ME", ai_generated=True, created_at=datetime.now(timezone.utc)
        )

        new_quiz_id = int(uuid.uuid4())
        db_quiz = Quiz(id=new_quiz_id, lesson_id=new_lesson_id, version=1, ai_generated=True, created_at=datetime.now(timezone.utc))

        # All models involved must be in the same region/account and use the same DynamoDB client.
        with TransactWrite() as transaction:
            transaction.save(db_lesson)
            transaction.save(practice_task)
            transaction.save(db_quiz)

        quiz_data = ai.generate_quiz(
            lesson_content=lesson_content,
            grade_level=grade_level,
            language=language_value,
        )

        for question_data in quiz_data["questions"]:
            db_quiz.add_question(
                question_text=question_data["question_text"],
                question_type=question_data["question_type"],
                options=question_data["options"],
                correct_answer=question_data["correct_answer"],
            )
        db_quiz.save()

        # db_lesson = Lesson.get(subject_id, new_lesson_id) # Fetch the saved lesson to return it

        return db_lesson  # Return the PynamoDB model instance

    except Exception as e:  # Catch specific PynamoDB exceptions if needed (e.g., PutError)
        # Handle rollback/compensation logic if partial creation occurred (DynamoDB is not transactional like SQL)
        # This is more complex in DynamoDB. Consider using DynamoDB Transactions for critical multi-item writes.
        print(f"Error in create_lesson_with_content: {e}")  # Use logging in production
        raise  # Re-raise or raise a custom service exception


def submit_quiz_responses(quiz_id: int, student_id: int, responses: List[schemas.QuizResponse]) -> schemas.QuizSubmissionResponse:
    try:
        try:
            quiz = Quiz.get(quiz_id)
        except Quiz.DoesNotExist:
            raise ValueError("Quiz not found")

        # Create quiz attempt
        # Assuming QuizAttempt PK is student_id (hash) + new unique id (range)
        new_attempt_id = int(uuid.uuid4())
        db_attempt = QuizAttempt(
            student_id=student_id,  # hash key
            id=new_attempt_id,  # range key
            quiz_id=quiz_id,  # Link to quiz
            start_time=datetime.now(timezone.utc),
            # end_time, score, passed will be set later
            passed=False,
            cheating_detected=False,
        )
        db_attempt.finish_attempt()
        db_attempt.save()  # Save initial attempt

        student_answers = []
        correct_answers = []

        # Process responses
        for response in responses:
            question_id = response.question_id
            answer = response.answer
            # Fetch question
            questions = {question.question_id:{"correct_answer": question.correct_answer}  for question in quiz.quiz_questions}
            question = questions.get(question_id)
            
            is_correct = answer.strip().lower() == question.correct_answer.strip().lower()

            db_attempt.add_response(
                question_id=question_id,  # Link to question
                student_answer=answer,
                is_correct=is_correct,
                points_earned= 1 if is_correct else 0,
            )
        db_attempt.calculate_score()
        db_attempt.save()  # Update the attempt record

        # Generate AI feedback (no DB interaction here)
        ai_feedback = ai.generate_quiz_feedback(student_answers=student_answers, correct_answers=correct_answers)

        # Regenerate quiz if needed
        regenerated_quiz = None
        if (not db_attempt.passed) and quiz.ai_generated:
            try:
                lesson = Lesson.get(quiz.lesson_id)  
                quizzes_for_lesson = list(Quiz.query(lesson.subject_id, filter_condition=Quiz.lesson_id == lesson.id)) # If GSI or appropriate key
                max_version = max(q.version_number for q in quizzes_for_lesson if q.lesson_id == lesson.id) if quizzes_for_lesson else 0

                new_version = max_version + 1  
                student = Student.get(student_id)
                new_quiz_data = ai.generate_quiz(
                    lesson_content=lesson.content,
                    grade_level=student.current_grade,  # Placeholder, get from lesson.subject.grade_level
                    language=student.language,  # Placeholder, get from lesson.subject.language
                )
                # Create new quiz
                new_quiz_id_2 = int(uuid.uuid4())
                new_quiz = Quiz(id=new_quiz_id_2, lesson_id=lesson.id, version=new_version, ai_generated=True, created_at=datetime.now(timezone.utc))
                new_quiz.save()

                # Create new questions
                for question_data in new_quiz_data["questions"]:
                    new_quiz.add_question(
                            question_text=question_data["question_text"],
                            question_type=question_data["question_type"],
                            options=question_data["options"],
                            correct_answer=question_data["correct_answer"],
                        )
                    
                new_quiz.save()

                regenerated_quiz = new_quiz  # Assign PynamoDB model

            except Lesson.DoesNotExist:
                print("Lesson not found for quiz during regeneration")  # Log appropriately
                # Handle if lesson not found, maybe don't regenerate
                regenerated_quiz = None
            except Exception as e:
                print(f"Error during quiz regeneration: {e}")  # Log appropriately
                regenerated_quiz = None  # Don't fail the whole submission


        # Example of constructing response data
        attempt_schema_data = schemas.QuizAttempt(
            id=db_attempt.id,
            quiz_id=db_attempt.quiz_id,
            student_id=db_attempt.student_id,
            start_time=db_attempt.start_time,
            end_time=db_attempt.end_time,
            score=db_attempt.score,
            passed=db_attempt.passed,
            quiz_version=quiz.version_number, 
            cheating_detected=db_attempt.cheating_detected,
            lesson_title=lesson.title
        )

        return schemas.QuizSubmissionResponse(
            attempt=attempt_schema_data,  # Pass the schema object
            ai_feedback=ai_feedback,
            regenerated_quiz=regenerated_quiz,  # This should ideally be a schema object too, convert if needed
        )

    except Exception as e:  # Catch PynamoDB exceptions, value errors, etc.
        print(f"Error in submit_quiz_responses: {e}")  # Use logging
        raise  # Re-raise or custom exception


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
    completed_lessons = 0  # Placeholder

    # --- Total Lessons (Complex) ---
    # Need: Total lessons in subjects the student is enrolled in.
    # Requires: Get student's enrollments (need Enrollment model and GSI?).
    #           For each enrollment, get subject_id.
    #           Count lessons for each subject_id (need GSI on Lesson.subject_id).
    total_lessons = 0  # Placeholder

    # --- Average Score (Moderate with GSI) ---
    # Need: Average of QuizAttempt.score for a student.
    # Requires: GSI on QuizAttempt with student_id as hash key.
    #           Query all attempts for student, sum scores, count, calculate average.
    avg_score = 0.0  # Placeholder

    # --- Streak (Very Complex) ---
    # Need: Consecutive days student passed a quiz.
    # Requires: GSI on QuizAttempt with student_id as hash key and date as sort key (or composite).
    #           Query attempts for student, ordered by date/time.
    #           Check if end_time dates are consecutive and passed=True.
    #           This is a non-trivial query pattern in DynamoDB.
    streak = 0  # Placeholder

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
