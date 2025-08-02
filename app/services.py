# app/services.py
from typing import List
from . import schemas  # Keep schemas
from .ai import generate_content as ai
from .models import Lesson, PracticeTask, Quiz, QuizAttempt, Student
from pynamodb.transactions import TransactWrite
from pynamodb.exceptions import TransactWriteError
from pynamodb.connection import Connection
from datetime import datetime, timezone  # Use timezone-aware datetime for DynamoDB
import uuid  # If using UUIDs or need unique IDs
from . import crud

def create_lesson_with_content(subject_id: str, grade_level:int, language_value:str, instructor_id: str, title: str) -> Lesson:  # Return PynamoDB model
    try:
        lesson_content = ai.generate_lesson(
            title=title,
            grade_level=grade_level,
            language=language_value,
        )

        new_lesson_id = str(uuid.uuid4())
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

        new_task_id = str(uuid.uuid4())
        practice_task = PracticeTask(
            id=new_task_id, lesson_id=new_lesson_id, title=title, content=task_content, difficulty="ME", ai_generated=True, created_at=datetime.now(timezone.utc)
        )

        new_quiz_id = str(uuid.uuid4())
        db_quiz = Quiz(id=new_quiz_id, lesson_id=new_lesson_id, title=title, version_number=1, ai_generated=True, created_at=datetime.now(timezone.utc))

        # All models involved must be in the same region/account and use the same DynamoDB client.
        conn = Connection(region='us-east-1')  # Adjust region as needed
        with TransactWrite(connection=conn) as transaction:
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
    except TransactWriteError as e:
        print(f"Transaction failed: {e}")  # Use logging in production
        raise ValueError("Failed to create lesson with content due to transaction error")
    except Exception as e:  # Catch specific PynamoDB exceptions if needed (e.g., PutError)
        # Handle rollback/compensation logic if partial creation occurred (DynamoDB is not transactional like SQL)
        # This is more complex in DynamoDB. Consider using DynamoDB Transactions for critical multi-item writes.
        print(f"Error in create_lesson_with_content: {e}")  # Use logging in production
        raise  # Re-raise or raise a custom service exception


def submit_quiz_responses(quiz_id: str, student_id: str, responses: List[schemas.QuizResponse]) -> schemas.QuizSubmissionResponse:
    try:
        try:
            quiz = Quiz.get(quiz_id)
        except Quiz.DoesNotExist:
            raise ValueError("Quiz not found")

        # Create quiz attempt
        previous_attempts = list(QuizAttempt.query(student_id, QuizAttempt.quiz_id == quiz_id))
        attempt_number = len(previous_attempts) + 1

        if quiz.max_attempts and attempt_number > quiz.max_attempts:
            raise ValueError("Exceeded maximum number of attempts")

        new_attempt_id = str(uuid.uuid4())
        db_attempt = QuizAttempt(
            student_id=student_id,  # hash key
            id=new_attempt_id,  # range key
            quiz_id=quiz_id,  # Link to quiz
            attempt_number=attempt_number,
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
            question = next((q for q in quiz.quiz_questions if q.question_id == question_id), None)
            
            if not question:
                # Or handle this case more gracefully
                raise ValueError(f"Question with id {question_id} not found in quiz {quiz_id}")

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
                lesson = Lesson.get(quiz.lesson_id) if quiz.lesson_id else None
                if lesson:
                    student = crud.crud_student.get_by_user_id(student_id) 
                    if student:
                        quizzes_for_lesson = list(Quiz.query(lesson.subject_id, filter_condition=Quiz.lesson_id == lesson.id))
                        max_version = max((q.version_number for q in quizzes_for_lesson if q.lesson_id == lesson.id), default=0)

                        new_version = max_version + 1
                        new_quiz_data = ai.generate_quiz(
                            lesson_content=lesson.content,
                            grade_level=student.current_grade,
                            language=student.language,
                        )
                        # Create new quiz
                        new_quiz_id_2 = str(uuid.uuid4())
                        new_quiz = Quiz(id=new_quiz_id_2, lesson_id=lesson.id, version_number=new_version, ai_generated=True, created_at=datetime.now(timezone.utc))
                        
                        # Create new questions
                        for question_data in new_quiz_data["questions"]:
                            new_quiz.add_question(
                                    question_text=question_data["question_text"],
                                    question_type=question_data["question_type"],
                                    options=question_data["options"],
                                    correct_answer=question_data["correct_answer"],
                                )
                        new_quiz.save()
                        regenerated_quiz = new_quiz

            except Lesson.DoesNotExist:
                print("Lesson not found for quiz during regeneration")
                regenerated_quiz = None
            except Student.DoesNotExist:
                print(f"Student with id {student_id} not found")
                regenerated_quiz = None
            except Exception as e:
                print(f"Error during quiz regeneration: {e}")
                regenerated_quiz = None

        lesson = Lesson.get(quiz.lesson_id) if quiz.lesson_id else None
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
            lesson_title=lesson.title if lesson else ""
        )

        return schemas.QuizSubmissionResponse(
            attempt=attempt_schema_data,
            ai_feedback=ai_feedback,
            regenerated_quiz=regenerated_quiz,
        )

    except Exception as e:
        print(f"Error in submit_quiz_responses: {e}")
        raise


def get_student_dashboard_stats(student_id: str) -> schemas.DashboardStats:
    # --- Completed Lessons ---
    passed_attempts = list(QuizAttempt.scan((QuizAttempt.student_id == student_id) & (QuizAttempt.passed == True)))
    completed_lesson_ids = set()
    for attempt in passed_attempts:
        try:
            quiz = Quiz.get(attempt.quiz_id)
            completed_lesson_ids.add(quiz.lesson_id)
        except Quiz.DoesNotExist:
            continue
    completed_lessons = len(completed_lesson_ids)

    # --- Total Lessons ---
    try:
        student = crud.crud_student.get_by_user_id(student_id)
        if student:
            enrolled_subject_ids = [e.subject_id for e in student.get_active_enrollments()]
            total_lessons = 0
            for subject_id in enrolled_subject_ids:
                total_lessons += Lesson.subject_index.count(subject_id)
        else:
            total_lessons = 0
    except Student.DoesNotExist:
        total_lessons = 0

    # --- Average Score ---
    all_attempts = list(QuizAttempt.scan(QuizAttempt.student_id == student_id))
    if not all_attempts:
        avg_score = 0.0
    else:
        total_score = sum(attempt.percentage_score for attempt in all_attempts if attempt.percentage_score is not None)
        avg_score = total_score / len(all_attempts) if all_attempts else 0.0

    # --- Streak ---
    passed_attempts.sort(key=lambda x: x.end_time, reverse=True)
    if not passed_attempts:
        streak = 0
    else:
        streak = 0
        if passed_attempts:
            dates = sorted(list(set(attempt.end_time.date() for attempt in passed_attempts)))
            if dates:
                longest_streak = 0
                current_streak = 1
                for i in range(1, len(dates)):
                    if (dates[i] - dates[i-1]).days == 1:
                        current_streak += 1
                    else:
                        longest_streak = max(longest_streak, current_streak)
                        current_streak = 1
                longest_streak = max(longest_streak, current_streak)
                streak = longest_streak

    return schemas.DashboardStats(
        completed_lessons=completed_lessons,
        total_lessons=total_lessons,
        avg_score=avg_score,
        streak=streak,
    )
