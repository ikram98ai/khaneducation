# Khan Education API Documentation

This document provides comprehensive documentation for the Khan Education API, designed for seamless integration with the React web application.

## Base URL

The base URL for the API is `http://localhost:8000`.

## Authentication

The API uses JSON Web Tokens (JWT) for authentication. To access protected endpoints, you must first obtain an `access_token` by sending a `POST` request to the `/login` endpoint with your user credentials.

Once you have the `access_token`, include it in the `Authorization` header of all subsequent requests in the format:

```
Authorization: Bearer <your_access_token>
```

## Endpoints

### 1. Auth

#### `POST /login`

*   **Description:** Authenticates a user and returns a JWT access token.
*   **Request Body:**
    ```json
    {
        "email": "user@example.com",
        "password": "your_password"
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer"
    }
    ```
*   **Error Responses:**
    *   **403 Forbidden:**
        ```json
        {
            "detail": "Invalid Credentials"
        }
        ```
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Database error"
        }
        ```

### 2. Admin (Requires Admin Role)

#### `POST /admin/users/`

*   **Description:** Creates a new user.
*   **Request Body:**
    ```json
    {
        "username": "newuser",
        "first_name": "John",
        "last_name": "Doe",
        "email": "newuser@example.com",
        "password": "StrongPassword123!"
    }
    ```
*   **Success Response (201 Created):**
    ```json
    {
        "username": "newuser",
        "first_name": "John",
        "last_name": "Doe",
        "email": "newuser@example.com",
        "role": "student",
        "id": 1
    }
    ```
*   **Error Responses:**
    *   **400 Bad Request:**
        ```json
        {
            "detail": "Email is already registered."
        }
        ```
        or
        ```json
        {
            "detail": "Username is already taken."
        }
        ```
        or
        ```json
        {
            "detail": "Password must be at least 8 characters long, and include at least one uppercase letter, one lowercase letter, one digit, and one special character."
        }
        ```
    *   **401 Unauthorized:** (If not authenticated as admin)
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Could not create user"
        }
        ```

#### `GET /admin/users/`

*   **Description:** Retrieves a list of all users.
*   **Query Parameters:**
    *   `skip` (int, optional): Number of items to skip (default: 0).
    *   `limit` (int, optional): Maximum number of items to return (default: 100).
*   **Success Response (200 OK):**
    ```json
    [
        {
            "username": "user1",
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice@example.com",
            "role": "student",
            "id": 1
        },
        {
            "username": "user2",
            "first_name": "Bob",
            "last_name": "Johnson",
            "email": "bob@example.com",
            "role": "instructor",
            "id": 2
        }
    ]
    ```
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated as admin)
    *   **404 Not Found:**
        ```json
        {
            "detail": "No users found"
        }
        ```
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Database error"
        }
        ```

#### `GET /admin/users/{user_id}`

*   **Description:** Retrieves a specific user by ID.
*   **Path Parameters:**
    *   `user_id` (int, required): The ID of the user to retrieve.
*   **Success Response (200 OK):**
    ```json
    {
        "username": "specificuser",
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane@example.com",
        "role": "student",
        "id": 3
    }
    ```
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated as admin)
    *   **404 Not Found:**
        ```json
        {
            "detail": "User not found"
        }
        ```
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Database error"
        }
        ```

#### `PUT /admin/users/{user_id}`

*   **Description:** Updates an existing user by ID.
*   **Path Parameters:**
    *   `user_id` (int, required): The ID of the user to update.
*   **Request Body:** (Partial updates are supported)
    ```json
    {
        "first_name": "Janet",
        "role": "instructor"
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
        "username": "specificuser",
        "first_name": "Janet",
        "last_name": "Doe",
        "email": "jane@example.com",
        "role": "instructor",
        "id": 3
    }
    ```
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated as admin)
    *   **404 Not Found:**
        ```json
        {
            "detail": "User not found"
        }
        ```
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Could not update item"
        }
        ```

#### `DELETE /admin/users/{user_id}`

*   **Description:** Deletes a user by ID.
*   **Path Parameters:**
    *   `user_id` (int, required): The ID of the user to delete.
*   **Success Response (200 OK):**
    ```json
    {
        "username": "deleteduser",
        "first_name": "Old",
        "last_name": "User",
        "email": "olduser@example.com",
        "role": "student",
        "id": 4
    }
    ```
    (Returns the deleted user object)
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated as admin)
    *   **404 Not Found:**
        ```json
        {
            "detail": "User not found"
        }
        ```
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Could not delete item"
        }
        ```

#### `POST /admin/subjects/`

*   **Description:** Creates a new subject.
*   **Request Body:**
    ```json
    {
        "name": "Mathematics",
        "description": "Study of numbers, quantity, and space.",
        "grade_level": 10,
        "language": "English"
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
        "name": "Mathematics",
        "description": "Study of numbers, quantity, and space.",
        "grade_level": 10,
        "language": "English",
        "id": 1,
        "total_lessons": 0,
        "completed_lessons": 0,
        "progress": 0.0
    }
    ```
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated as admin)
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Could not create item"
        }
        ```

#### `GET /admin/subjects/`

*   **Description:** Retrieves a list of all subjects.
*   **Query Parameters:**
    *   `skip` (int, optional): Number of items to skip (default: 0).
    *   `limit` (int, optional): Maximum number of items to return (default: 100).
*   **Success Response (200 OK):**
    ```json
    [
        {
            "name": "Mathematics",
            "description": "Study of numbers, quantity, and space.",
            "grade_level": 10,
            "language": "English",
            "id": 1,
            "total_lessons": 5,
            "completed_lessons": 2,
            "progress": 40.0
        }
    ]
    ```
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated as admin)
    *   **404 Not Found:**
        ```json
        {
            "detail": "No subjects found"
        }
        ```
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Database error"
        }
        ```

#### `PUT /admin/subjects/{subject_id}`

*   **Description:** Updates an existing subject by ID.
*   **Path Parameters:**
    *   `subject_id` (int, required): The ID of the subject to update.
*   **Request Body:** (Partial updates are supported)
    ```json
    {
        "description": "Advanced study of numbers."
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
        "name": "Mathematics",
        "description": "Advanced study of numbers.",
        "grade_level": 10,
        "language": "English",
        "id": 1,
        "total_lessons": 5,
        "completed_lessons": 2,
        "progress": 40.0
    }
    ```
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated as admin)
    *   **404 Not Found:**
        ```json
        {
            "detail": "Subject not found"
        }
        ```
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Could not update item"
        }
        ```

#### `DELETE /admin/subjects/{subject_id}`

*   **Description:** Deletes a subject by ID.
*   **Path Parameters:**
    *   `subject_id` (int, required): The ID of the subject to delete.
*   **Success Response (200 OK):**
    ```json
    {
        "name": "Mathematics",
        "description": "Study of numbers, quantity, and space.",
        "grade_level": 10,
        "language": "English",
        "id": 1,
        "total_lessons": 0,
        "completed_lessons": 0,
        "progress": 0.0
    }
    ```
    (Returns the deleted subject object)
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated as admin)
    *   **404 Not Found:**
        ```json
        {
            "detail": "Subject not found"
        }
        ```
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Could not delete item"
        }
        ```

#### `POST /admin/subjects/{subject_id}/lessons/`

*   **Description:** Creates a new lesson for a specific subject.
*   **Path Parameters:**
    *   `subject_id` (int, required): The ID of the subject to associate the lesson with.
*   **Request Body:**
    ```json
    {
        "title": "Introduction to Algebra",
        "content": "This lesson covers basic algebraic concepts."
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
        "subject_id": 1,
        "title": "Introduction to Algebra",
        "content": "This lesson covers basic algebraic concepts.",
        "id": 1,
        "instructor_id": 1,
        "status": "DR",
        "created_at": "2024-07-14T12:00:00Z",
        "verified_at": null,
        "progress": 0.0
    }
    ```
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated as admin)
    *   **404 Not Found:**
        ```json
        {
            "detail": "Subject not found"
        }
        ```
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Could not create item"
        }
        ```

#### `GET /admin/subjects/{subject_id}/lessons/`

*   **Description:** Retrieves a list of all lessons for a specific subject.
*   **Path Parameters:**
    *   `subject_id` (int, required): The ID of the subject whose lessons to retrieve.
*   **Query Parameters:**
    *   `skip` (int, optional): Number of items to skip (default: 0).
    *   `limit` (int, optional): Maximum number of items to return (default: 100).
*   **Success Response (200 OK):**
    ```json
    [
        {
            "subject_id": 1,
            "title": "Introduction to Algebra",
            "content": "This lesson covers basic algebraic concepts.",
            "id": 1,
            "instructor_id": 1,
            "status": "DR",
            "created_at": "2024-07-14T12:00:00Z",
            "verified_at": null,
            "progress": 0.0
        }
    ]
    ```
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated as admin)
    *   **404 Not Found:**
        ```json
        {
            "detail": "Subject not found"
        }
        ```
        or
        ```json
        {
            "detail": "No lessons found for this subject"
        }
        ```
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Database error"
        }
        ```

#### `GET /admin/lessons/{lesson_id}`

*   **Description:** Retrieves a specific lesson by ID.
*   **Path Parameters:**
    *   `lesson_id` (int, required): The ID of the lesson to retrieve.
*   **Success Response (200 OK):**
    ```json
    {
        "subject_id": 1,
        "title": "Introduction to Algebra",
        "content": "This lesson covers basic algebraic concepts.",
        "id": 1,
        "instructor_id": 1,
        "status": "DR",
        "created_at": "2024-07-14T12:00:00Z",
        "verified_at": null,
        "progress": 0.0
    }
    ```
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated as admin)
    *   **404 Not Found:**
        ```json
        {
            "detail": "Lesson not found"
        }
        ```
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Database error"
        }
        ```

#### `PUT /admin/lessons/{lesson_id}`

*   **Description:** Updates an existing lesson by ID.
*   **Path Parameters:**
    *   `lesson_id` (int, required): The ID of the lesson to update.
*   **Request Body:** (Partial updates are supported)
    ```json
    {
        "title": "Updated Algebra Introduction"
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
        "subject_id": 1,
        "title": "Updated Algebra Introduction",
        "content": "This lesson covers basic algebraic concepts.",
        "id": 1,
        "instructor_id": 1,
        "status": "DR",
        "created_at": "2024-07-14T12:00:00Z",
        "verified_at": null,
        "progress": 0.0
    }
    ```
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated as admin)
    *   **404 Not Found:**
        ```json
        {
            "detail": "Lesson not found"
        }
        ```
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Could not update item"
        }
        ```

#### `DELETE /admin/lessons/{lesson_id}`

*   **Description:** Deletes a lesson by ID.
*   **Path Parameters:**
    *   `lesson_id` (int, required): The ID of the lesson to delete.
*   **Success Response (200 OK):**
    ```json
    {
        "subject_id": 1,
        "title": "Introduction to Algebra",
        "content": "This lesson covers basic algebraic concepts.",
        "id": 1,
        "instructor_id": 1,
        "status": "DR",
        "created_at": "2024-07-14T12:00:00Z",
        "verified_at": null,
        "progress": 0.0
    }
    ```
    (Returns the deleted lesson object)
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated as admin)
    *   **404 Not Found:**
        ```json
        {
            "detail": "Lesson not found"
        }
        ```
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Could not delete item"
        }
        ```

#### `POST /admin/lessons/{lesson_id}/practice_tasks/`

*   **Description:** Creates a new practice task for a specific lesson.
*   **Path Parameters:**
    *   `lesson_id` (int, required): The ID of the lesson to associate the practice task with.
*   **Request Body:**
    ```json
    {
        "content": "Solve for x: 2x + 5 = 15",
        "difficulty": "MEDIUM"
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
        "lesson_id": 1,
        "content": "Solve for x: 2x + 5 = 15",
        "difficulty": "MEDIUM",
        "id": 1,
        "ai_generated": true,
        "created_at": "2024-07-14T12:00:00Z"
    }
    ```
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated as admin)
    *   **404 Not Found:**
        ```json
        {
            "detail": "Lesson not found"
        }
        ```
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Could not create item"
        }
        ```

#### `GET /admin/lessons/{lesson_id}/practice_tasks/`

*   **Description:** Retrieves a list of all practice tasks for a specific lesson.
*   **Path Parameters:**
    *   `lesson_id` (int, required): The ID of the lesson whose practice tasks to retrieve.
*   **Query Parameters:**
    *   `skip` (int, optional): Number of items to skip (default: 0).
    *   `limit` (int, optional): Maximum number of items to return (default: 100).
*   **Success Response (200 OK):**
    ```json
    [
        {
            "lesson_id": 1,
            "content": "Solve for x: 2x + 5 = 15",
            "difficulty": "MEDIUM",
            "id": 1,
            "ai_generated": true,
            "created_at": "2024-07-14T12:00:00Z"
        }
    ]
    ```
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated as admin)
    *   **404 Not Found:**
        ```json
        {
            "detail": "Lesson not found"
        }
        ```
        or
        ```json
        {
            "detail": "No tasks found for this lesson"
        }
        ```
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Database error"
        }
        ```

#### `POST /admin/lessons/{lesson_id}/quizzes/`

*   **Description:** Creates a new quiz for a specific lesson.
*   **Path Parameters:**
    *   `lesson_id` (int, required): The ID of the lesson to associate the quiz with.
*   **Request Body:**
    ```json
    {
        "version": 1
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
        "lesson_id": 1,
        "version": 1,
        "id": 1,
        "ai_generated": true,
        "created_at": "2024-07-14T12:00:00Z",
        "questions": []
    }
    ```
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated as admin)
    *   **404 Not Found:**
        ```json
        {
            "detail": "Lesson not found"
        }
        ```
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Could not create item"
        }
        ```

#### `GET /admin/lessons/{lesson_id}/quizzes/`

*   **Description:** Retrieves a list of all quizzes for a specific lesson.
*   **Path Parameters:**
    *   `lesson_id` (int, required): The ID of the lesson whose quizzes to retrieve.
*   **Query Parameters:**
    *   `skip` (int, optional): Number of items to skip (default: 0).
    *   `limit` (int, optional): Maximum number of items to return (default: 100).
*   **Success Response (200 OK):**
    ```json
    [
        {
            "lesson_id": 1,
            "version": 1,
            "id": 1,
            "ai_generated": true,
            "created_at": "2024-07-14T12:00:00Z",
            "questions": []
        }
    ]
    ```
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated as admin)
    *   **404 Not Found:**
        ```json
        {
            "detail": "Lesson not found"
        }
        ```
        or
        ```json
        {
            "detail": "No quizzes found for this lesson"
        }
        ```
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Database error"
        }
        ```

### 3. Dashboard

#### `GET /dashboard/student`

*   **Description:** Retrieves the dashboard information for the current student.
*   **Success Response (200 OK):**
    ```json
    {
        "student": {
            "user_id": 1,
            "language": "English",
            "current_grade": 10
        },
        "enrollments": [
            {
                "id": 1,
                "student_id": 1,
                "subject_id": 1,
                "enrolled_at": "2024-07-14T12:00:00Z"
            }
        ],
        "recent_attempts": [
            {
                "quiz_id": 1,
                "student_id": 1,
                "id": 1,
                "start_time": "2024-07-14T12:00:00Z",
                "end_time": "2024-07-14T12:10:00Z",
                "score": 85.5,
                "passed": true,
                "cheating_detected": false
            }
        ],
        "practice_tasks": [
            {
                "lesson_id": 1,
                "content": "Solve for x: 2x + 5 = 15",
                "difficulty": "MEDIUM",
                "id": 1,
                "ai_generated": true,
                "created_at": "2024-07-14T12:00:00Z"
            }
        ]
    }
    ```
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated as a student)
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Database error"
        }
        ```

#### `GET /dashboard/student/stats`

*   **Description:** Retrieves statistical data for the current student's dashboard.
*   **Success Response (200 OK):**
    ```json
    {
        "completedLessons": 10,
        "totalLessons": 15,
        "avgScore": 75.2,
        "streak": 5
    }
    ```
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated as a student)
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Database error"
        }
        ```

#### `GET /dashboard/admin`

*   **Description:** Retrieves dashboard information for administrators.
*   **Success Response (200 OK):**
    ```json
    {
        "total_students": 100,
        "total_lessons": 500,
        "total_subjects": 10,
        "total_quizzes": 200,
        "recent_lessons": [
            {
                "subject_id": 1,
                "title": "Recent Lesson 1",
                "content": "...",
                "id": 10,
                "instructor_id": 1,
                "status": "VE",
                "created_at": "2024-07-13T10:00:00Z",
                "verified_at": "2024-07-13T11:00:00Z",
                "progress": 100.0
            }
        ],
        "recent_attempts": [
            {
                "quiz_id": 5,
                "student_id": 20,
                "id": 50,
                "start_time": "2024-07-13T09:00:00Z",
                "end_time": "2024-07-13T09:30:00Z",
                "score": 90.0,
                "passed": true,
                "cheating_detected": false
            }
        ]
    }
    ```
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated as admin)
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Database error"
        }
        ```

### 4. Lessons

#### `POST /subjects/{subject_id}/lessons/`

*   **Description:** Creates a new lesson for a specific subject.
*   **Path Parameters:**
    *   `subject_id` (int, required): The ID of the subject to associate the lesson with.
*   **Request Body:**
    ```json
    {
        "title": "New Lesson Title",
        "content": "Content of the new lesson."
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
        "subject_id": 1,
        "title": "New Lesson Title",
        "content": "Content of the new lesson.",
        "id": 2,
        "instructor_id": 1,
        "status": "DR",
        "created_at": "2024-07-14T13:00:00Z",
        "verified_at": null,
        "progress": 0.0
    }
    ```
*   **Error Responses:**
    *   **400 Bad Request:**
        ```json
        {
            "detail": "Error message from service (e.g., 'Subject not found')"
        }
        ```
    *   **401 Unauthorized:** (If not authenticated)
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Database error"
        }
        ```

#### `GET /subjects/{subject_id}/lessons/`

*   **Description:** Retrieves a list of all lessons for a specific subject.
*   **Path Parameters:**
    *   `subject_id` (int, required): The ID of the subject whose lessons to retrieve.
*   **Query Parameters:**
    *   `skip` (int, optional): Number of items to skip (default: 0).
    *   `limit` (int, optional): Maximum number of items to return (default: 100).
*   **Success Response (200 OK):**
    ```json
    [
        {
            "subject_id": 1,
            "title": "Lesson 1 for Subject 1",
            "content": "...",
            "id": 1,
            "instructor_id": 1,
            "status": "DR",
            "created_at": "2024-07-14T12:00:00Z",
            "verified_at": null,
            "progress": 0.0
        }
    ]
    ```
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated)
    *   **404 Not Found:**
        ```json
        {
            "detail": "No lessons found for this subject"
        }
        ```
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Database error"
        }
        ```

#### `PUT /subjects/{subject_id}/lessons/{lesson_id}/verify`

*   **Description:** Verifies a lesson, changing its status to 'VERIFIED'.
*   **Path Parameters:**
    *   `subject_id` (int, required): The ID of the subject the lesson belongs to.
    *   `lesson_id` (int, required): The ID of the lesson to verify.
*   **Success Response (200 OK):**
    ```json
    {
        "subject_id": 1,
        "title": "Lesson Title",
        "content": "...",
        "id": 1,
        "instructor_id": 1,
        "status": "VE",
        "created_at": "2024-07-14T12:00:00Z",
        "verified_at": "2024-07-14T14:00:00Z",
        "progress": 0.0
    }
    ```
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated)
    *   **404 Not Found:**
        ```json
        {
            "detail": "Lesson not found"
        }
        ```
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Database error"
        }
        ```

### 5. Quizzes

#### `POST /quizzes/submit`

*   **Description:** Submits a student's responses to a quiz.
*   **Request Body:**
    ```json
    {
        "quiz_id": 1,
        "responses": [
            {
                "question_id": 101,
                "student_answer": "Answer to question 1"
            },
            {
                "question_id": 102,
                "student_answer": "Answer to question 2"
            }
        ]
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
        "message": "Quiz submitted successfully",
        "attempt_id": 123,
        "score": 85.5,
        "passed": true
    }
    ```
*   **Error Responses:**
    *   **400 Bad Request:**
        ```json
        {
            "detail": "Error message from service (e.g., 'Quiz not found', 'Invalid responses')"
        }
        ```
    *   **401 Unauthorized:** (If not authenticated as a student)
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Database error"
        }
        ```

#### `GET /quizzes/attempts`

*   **Description:** Retrieves a list of all quiz attempts, optionally filtered by student ID.
*   **Query Parameters:**
    *   `student_id` (int, optional): Filter attempts by a specific student ID.
    *   `skip` (int, optional): Number of items to skip (default: 0).
    *   `limit` (int, optional): Maximum number of items to return (default: 100).
*   **Success Response (200 OK):**
    ```json
    [
        {
            "quiz_id": 1,
            "student_id": 1,
            "id": 1,
            "start_time": "2024-07-14T12:00:00Z",
            "end_time": "2024-07-14T12:10:00Z",
            "score": 85.5,
            "passed": true,
            "cheating_detected": false
        }
    ]
    ```
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated)
    *   **404 Not Found:**
        ```json
        {
            "detail": "No quiz attempts found"
        }
        ```
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Database error"
        }
        ```

#### `GET /quizzes/attempts/{attempt_id}`

*   **Description:** Retrieves a specific quiz attempt by ID.
*   **Path Parameters:**
    *   `attempt_id` (int, required): The ID of the quiz attempt to retrieve.
*   **Success Response (200 OK):**
    ```json
    {
        "quiz_id": 1,
        "student_id": 1,
        "id": 1,
        "start_time": "2024-07-14T12:00:00Z",
        "end_time": "2024-07-14T12:10:00Z",
        "score": 85.5,
        "passed": true,
        "cheating_detected": false
    }
    ```
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated)
    *   **404 Not Found:**
        ```json
        {
            "detail": "Attempt not found"
        }
        ```
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Database error"
        }
        ```

### 6. Subjects

#### `POST /subjects/`

*   **Description:** Creates a new subject.
*   **Request Body:**
    ```json
    {
        "name": "History",
        "description": "Study of past events.",
        "grade_level": 9,
        "language": "English"
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
        "name": "History",
        "description": "Study of past events.",
        "grade_level": 9,
        "language": "English",
        "id": 2,
        "total_lessons": 0,
        "completed_lessons": 0,
        "progress": 0.0
    }
    ```
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated)
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Could not create item"
        }
        ```

#### `GET /subjects/`

*   **Description:** Retrieves a list of all subjects.
*   **Query Parameters:**
    *   `skip` (int, optional): Number of items to skip (default: 0).
    *   `limit` (int, optional): Maximum number of items to return (default: 100).
*   **Success Response (200 OK):**
    ```json
    [
        {
            "name": "History",
            "description": "Study of past events.",
            "grade_level": 9,
            "language": "English",
            "id": 2,
            "total_lessons": 3,
            "completed_lessons": 1,
            "progress": 33.33
        }
    ]
    ```
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated)
    *   **404 Not Found:**
        ```json
        {
            "detail": "No subjects found"
        }
        ```
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Database error"
        }
        ```

#### `GET /subjects/{subject_id}`

*   **Description:** Retrieves a specific subject by ID.
*   **Path Parameters:**
    *   `subject_id` (int, required): The ID of the subject to retrieve.
*   **Success Response (200 OK):**
    ```json
    {
        "name": "History",
        "description": "Study of past events.",
        "grade_level": 9,
        "language": "English",
        "id": 2,
        "total_lessons": 3,
        "completed_lessons": 1,
        "progress": 33.33
    }
    ```
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated)
    *   **404 Not Found:**
        ```json
        {
            "detail": "Subject not found"
        }
        ```
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Database error"
        }
        ```

### 7. Users

#### `POST /users/`

*   **Description:** Creates a new user.
*   **Request Body:**
    ```json
    {
        "username": "newstudent",
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice.smith@example.com",
        "password": "SecurePassword123!"
    }
    ```
*   **Success Response (201 Created):**
    ```json
    {
        "username": "newstudent",
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice.smith@example.com",
        "role": "student",
        "id": 5
    }
    ```
*   **Error Responses:**
    *   **400 Bad Request:**
        ```json
        {
            "detail": "Email is already registered."
        }
        ```
        or
        ```json
        {
            "detail": "Username is already taken."
        }
        ```
        or
        ```json
        {
            "detail": "Password must be at least 8 characters long, and include at least one uppercase letter, one lowercase letter, one digit, and one special character."
        }
        ```
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Could not create user"
        }
        ```

#### `POST /users/profile/me`

*   **Description:** Creates a student profile for the currently authenticated user.
*   **Request Body:**
    ```json
    {
        "language": "English",
        "current_grade": 10
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
        "user": {
            "username": "currentuser",
            "first_name": "Current",
            "last_name": "User",
            "email": "current@example.com",
            "role": "student",
            "id": 1
        },
        "student_profile": {
            "user_id": 1,
            "language": "English",
            "current_grade": 10
        }
    }
    ```
*   **Error Responses:**
    *   **400 Bad Request:**
        ```json
        {
            "detail": "Student profile already exists for this user"
        }
        ```
    *   **401 Unauthorized:** (If not authenticated)
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Could not create student profile"
        }
        ```

#### `GET /users/profile/me`

*   **Description:** Retrieves the profile information for the currently authenticated user (including student profile if available).
*   **Success Response (200 OK):**
    ```json
    {
        "user": {
            "id": 1,
            "username": "currentuser",
            "first_name": "Current",
            "last_name": "User",
            "role": "student",
            "email": "current@example.com"
        },
        "student_profile": {
            "user_id": 1,
            "language": "English",
            "current_grade": 10
        }
    }
    ```
    (If no student profile exists, `student_profile` will be `null`)
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated)
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Database error"
        }
        ```

#### `PUT /users/profile/me`

*   **Description:** Updates the profile information for the currently authenticated user.
*   **Request Body:** (Partial updates are supported)
    ```json
    {
        "first_name": "Alice Updated",
        "email": "alice.updated@example.com"
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
        "username": "currentuser",
        "first_name": "Alice Updated",
        "last_name": "Smith",
        "email": "alice.updated@example.com",
        "role": "student",
        "id": 1
    }
    ```
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated)
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Could not update profile"
        }
        ```

#### `GET /users/{id}`

*   **Description:** Retrieves a specific user's profile by ID.
*   **Path Parameters:**
    *   `id` (int, required): The ID of the user to retrieve.
*   **Success Response (200 OK):**
    ```json
    {
        "user": {
            "id": 1,
            "username": "someuser",
            "first_name": "Some",
            "last_name": "User",
            "role": "student",
            "email": "some@example.com"
        },
        "student_profile": {
            "user_id": 1,
            "language": "English",
            "current_grade": 10
        }
    }
    ```
    (If no student profile exists, `student_profile` will be `null`)
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated)
    *   **404 Not Found:**
        ```json
        {
            "detail": "User with id: {id} does not exist"
        }
        ```
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Database error"
        }
        ```

#### `PUT /users/{id}`

*   **Description:** Updates a specific user's information by ID.
*   **Path Parameters:**
    *   `id` (int, required): The ID of the user to update.
*   **Request Body:** (Partial updates are supported)
    ```json
    {
        "first_name": "UpdatedName",
        "role": "instructor"
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
        "username": "someuser",
        "first_name": "UpdatedName",
        "last_name": "User",
        "email": "some@example.com",
        "role": "instructor",
        "id": 1
    }
    ```
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated)
    *   **404 Not Found:**
        ```json
        {
            "detail": "User with id: {id} does not exist"
        }
        ```
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Could not update user"
        }
        ```

#### `DELETE /users/{id}`

*   **Description:** Deletes a user by ID.
*   **Path Parameters:**
    *   `id` (int, required): The ID of the user to delete.
*   **Success Response (204 No Content):** (No response body)
*   **Error Responses:**
    *   **401 Unauthorized:** (If not authenticated)
    *   **404 Not Found:**
        ```json
        {
            "detail": "user with id: {id} does not exist"
        }
        ```
    *   **500 Internal Server Error:**
        ```json
        {
            "detail": "Could not delete user"
        }
        ```