# 🧠 AI Educational Backend (Fastapi)

This backend powers the AI Educational System UI and provides robust RESTful APIs to support role-based educational workflows for Admin (staff), Students, and AI Agents.

## 🔧 Core Features

*   **User Roles & Permissions**: Support for instructor, student, and AI agent roles with scoped access and views.
*   **Lesson Management API**: Admin (staff) can create, edit, and publish lessons with metadata like subject, grade, language, and status.
*   **Task & Quiz APIs**: Endpoints to manage student practice tasks and quizzes, including submissions and results.
*   **Analytics Endpoints**: Provide insights into student performance, lesson engagement, and system usage.
*   **AI Agent Interfaces**: APIs to integrate chat-based guidance, hint generation, and feedback mechanisms with AI models.

## 🛠 Tech Stack

*   Fastapi
*   PostgreSQL
*   JWT / Token Authentication
*   Celery + Redis (optional for async processing)
*   OpenAI / LangChain for AI capabilities

---

## API Documentation

### Authentication

The API uses token-based authentication with Djoser and Simple JWT. Users must be authenticated to access most endpoints.

### Roles

-   **Admin (staff):** Can create, manage, and view subject, lessons, practice tasks, and quizzes.
-   **Student:** Can view and interact with published lessons, take quizzes, and track their progress.

---

## Endpoints

### Authentication

-   **`POST /auth/users/`**
    -   **Description:** Register a new user.
    -   **Permissions:** AllowAny
    -   **Request Body:**
        ```json
        {
            "username": "",
            "password": "",
            "email": "",
            "first_name": "",
            "last_name": "",
            "dp": null
        }
        ```
    -   **Response:**
        ```json
        {
          "username": "",
          "email": "",
          "is_staff": false,
          "first_name": "",
          "last_name": "",
          "dp": null        
        }
        ```

-   **`POST /auth/jwt/create/`**
    -   **Description:** Authenticate a user and receive JWT tokens.
    -   **Permissions:** AllowAny
    -   **Request Body:**
        ```json
        {
          "email": "user@example.com",
          "password": "strongpassword"
        }
        ```
    -   **Response:**
        ```json
        {
          "access": "<access_token>",
          "refresh": "<refresh_token>"
        }
        ```

-   **`POST /auth/jwt/refresh/`**
    -   **Description:** Refresh an access token.
    -   **Permissions:** AllowAny
    -   **Request Body:**
        ```json
        {
          "refresh": "<refresh_token>"
        }
        ```
    -   **Response:**
        ```json
        {
          "access": "<new_access_token>"
        }
        ```

-   **`GET /auth/users/me/`**
    -   **Description:** Retrieve the current user's details.
    -   **Permissions:** IsAuthenticated
    -   **Response:**
        ```json
        {
          "id": 2,
          "username": "test",
          "email": "test@gmail.co",
          "is_staff": false,
          "first_name": "test",
          "last_name": "Khan",
          "dp": null
        }
        ```

-   **`PUT /auth/users/me/`**
    -   **Description:** Update the current user's details.
    -   **Permissions:** IsAuthenticated
    -   **Request Body:**
        ```json
        {
          "username": "test",
          "first_name": "test",
          "last_name": "Khan",
          "dp": null       
        }
        ```
    -   **Response:** (Same as `GET /auth/users/me/`)
  
    **`POST /auth/users/set_email/`**
    -   **Description:** Set a new email for the current user.
    -   **Permissions:** IsAuthenticated
    -   **Request Body:**
        ```json
        {
          "current_password": "current_password",
          "new_email": "new_email"
        }
        ```
    -   **Response:** `204 No Content`

### Subjects

-   **`GET /subjects/`**
    -   **Description:** Retrieve a list of all subjects.
    -   **Permissions:** IsAuthenticated
    -   **Query Parameters:**
        - `grade_level` (integer)
        - `grade_level__gte` (integer)
        - `grade_level__lte` (integer)
        - `language__icontains` (string)
        - `language__in` (array of strings)
        - `ordering` (string)
        - `page` (integer)
        - `search` (string)
    -   **Response:**
        ```json
        {
          "count": 123,
          "next": "http://api.example.org/subjects/?page=4",
          "previous": "http://api.example.org/subjects/?page=2",
          "results": [
            {
              "id": 0,
              "name": "string",
              "description": "string",
              "grade_level": 12,
              "language": "EN"
            }
          ]
        }
        ```

-   **`POST /subjects/`**
    -   **Description:** Create a new subject.
    -   **Permissions:** IsStaffOrAdmin
    -   **Request Body:**
        ```json
        {
            "name": "Science",
            "description": "The study of the natural and physical world.",
            "grade_level": "GR8",
            "language": "EN"
        }
        ```
    -   **Response:** (Same as `GET /subjects/` for a single object)

-   **`GET /subjects/{id}/`**
    -   **Description:** Retrieve a specific subject by its ID.
    -   **Permissions:** IsAuthenticated
    -   **Response:** (Same as `GET /subjects/` for a single object)

-   **`PUT /subjects/{id}/`**
    -   **Description:** Update a specific subject.
    -   **Permissions:** IsStaffOrAdmin
    -   **Request Body:** (Same as `POST /subjects/`)
    -   **Response:** (Same as `GET /subjects/` for a single object)

-   **`PATCH /subjects/{id}/`**
    -   **Description:** Partially update a specific subject.
    -   **Permissions:** IsStaffOrAdmin
    -   **Request Body:** (Partial data from `POST /subjects/`)
    -   **Response:** (Same as `GET /subjects/` for a single object)

-   **`DELETE /subjects/{id}/`**
    -   **Description:** Delete a specific subject.
    -   **Permissions:** IsStaffOrAdmin
    -   **Response:** `204 No Content`

### Languages

-   **`GET /languages/`**
    -   **Description:** Retrieve a list of all languages.
    -   **Permissions:** IsAuthenticated
    -   **Response:**
        ```json
        [
            {
                "code": "EN",
                "name": "English"
            },
            {
                "code": "ES",
                "name": "Spanish"
            }
        ]
        ```

### Lessons

-   **`GET /subjects/{subject_pk}/lessons/`**
    -   **Description:** Retrieve a list of lessons for a specific subject.
    -   **Permissions:** IsAuthenticated, IsEnrolledStudent
    -   **Response:**
        ```json
        [
            {
                "id": 1,
                "instructor": "instructor_username",
                "subject": "Mathematics",
                "title": "Introduction to Algebra",
                "content": "...",
                "status": "PU",
                "created_at": "...",
                "verified_at": "..."
            }
        ]
        ```

-   **`POST /subjects/{subject_pk}/lessons/`**
    -   **Description:** Create a new lesson for a subject. The content, practice task, and quiz are generated by an AI.
    -   **Permissions:** IsStaffOrAdmin
    -   **Request Body:**
        ```json
        {
            "title": "New Lesson Title"
        }
        ```
    -   **Response:** (Same as `GET /subjects/{subject_pk}/lessons/` for a single object)

-   **`GET /subjects/{subject_pk}/lessons/{id}/`**
    -   **Description:** Retrieve a specific lesson.
    -   **Permissions:** IsAuthenticated, IsEnrolledStudent
    -   **Response:** (Same as `GET /subjects/{subject_pk}/lessons/` for a single object)

-   **`PUT /subjects/{subject_pk}/lessons/{id}/`**
    -   **Description:** Update a specific lesson.
    -   **Permissions:** IsStaffOrAdmin
    -   **Request Body:**
        ```json
        {
            "title": "Updated Lesson Title",
            "content": "Updated content..."
        }
        ```
    -   **Response:** (Same as `GET /subjects/{subject_pk}/lessons/` for a single object)

-   **`PATCH /subjects/{subject_pk}/lessons/{id}/`**
    -   **Description:** Partially update a specific lesson.
    -   **Permissions:** IsStaffOrAdmin
    -   **Request Body:** (Partial data from `PUT /subjects/{subject_pk}/lessons/{id}/`)
    -   **Response:** (Same as `GET /subjects/{subject_pk}/lessons/` for a single object)

-   **`DELETE /subjects/{subject_pk}/lessons/{id}/`**
    -   **Description:** Delete a specific lesson.
    -   **Permissions:** IsStaffOrAdmin
    -   **Response:** `204 No Content`

-   **`GET /subjects/{subject_pk}/lessons/{id}/verify/`**
    -   **Description:** Verify a lesson.
    -   **Permissions:** IsStaffOrAdmin
    -   **Response:**
        ```json
        {
            "status": "verified",
            "verified_at": "..."
        }
        ```

### Quizzes

-   **`GET /subjects/{subject_pk}/lessons/{lesson_pk}/quizzes/`**
    -   **Description:** Retrieve a list of quizzes for a specific lesson.
    -   **Permissions:** IsAuthenticated, IsEnrolledStudent
    -   **Response:**
        ```json
        [
            {
                "id": 1,
                "lesson": 1,
                "lesson_title": "Introduction to Algebra",
                "version": 1,
                "questions": [   
                    {
                        "id": 0,
                        "question_text": "string",
                        "correct_answer": "string"
                    }
                ],
                "ai_generated": true,
                "created_at": "..."
            }
        ]
        ```

-   **`GET /subjects/{subject_pk}/lessons/{lesson_pk}/quizzes/{id}/`**
    -   **Description:** Retrieve a specific quiz.
    -   **Permissions:** IsAuthenticated, IsEnrolledStudent
    -   **Response:** (Same as `GET /subjects/{subject_pk}/lessons/{lesson_pk}/quizzes/` for a single object)


### Practice Tasks

-   **`GET /subjects/{subject_pk}/lessons/{lesson_pk}/tasks/`**
    -   **Description:** Retrieve a list of practice tasks for a specific lesson.
    -   **Permissions:** IsAuthenticated, IsEnrolledStudent
    -   **Response:**
        ```json
        [
            {
                "id": 1,
                "lesson": 1,
                "lesson_title": "Introduction to Algebra",
                "content": "...",
                "difficulty": "ME",
                "ai_generated": true,
                "created_at": "..."
            }
        ]
        ```

-   **`POST /subjects/{subject_pk}/lessons/{lesson_pk}/tasks/`**
    -   **Description:** Create a new practice task for a lesson.
    -   **Permissions:** IsStaffOrAdmin
    -   **Request Body:**
        ```json
        {
            "content": "New task content...",
            "difficulty": "EA"
        }
        ```
    -   **Response:** (Same as `GET /subjects/{subject_pk}/lessons/{lesson_pk}/tasks/` for a single object)

-   **`GET /subjects/{subject_pk}/lessons/{lesson_pk}/tasks/{id}/`**
    -   **Description:** Retrieve a specific practice task.
    -   **Permissions:** IsAuthenticated, IsEnrolledStudent
    -   **Response:** (Same as `GET /subjects/{subject_pk}/lessons/{lesson_pk}/tasks/` for a single object)

-   **`PUT /subjects/{subject_pk}/lessons/{lesson_pk}/tasks/{id}/`**
    -   **Description:** Update a specific practice task.
    -   **Permissions:** IsStaffOrAdmin
    -   **Request Body:**
        ```json
        {
            "content": "Updated task content...",
            "difficulty": "HA"
        }
        ```
    -   **Response:** (Same as `GET /subjects/{subject_pk}/lessons/{lesson_pk}/tasks/` for a single object)

-   **`PATCH /subjects/{subject_pk}/lessons/{lesson_pk}/tasks/{id}/`**
    -   **Description:** Partially update a specific practice task.
    -   **Permissions:** IsStaffOrAdmin
    -   **Request Body:** (Partial data from `PUT /subjects/{subject_pk}/lessons/{lesson_pk}/tasks/{id}/`)
    -   **Response:** (Same as `GET /subjects/{subject_pk}/lessons/{lesson_pk}/tasks/` for a single object)

-   **`DELETE /subjects/{subject_pk}/lessons/{lesson_pk}/tasks/{id}/`**
    -   **Description:** Delete a specific practice task.
    -   **Permissions:** IsStaffOrAdmin
    -   **Response:** `204 No Content`

### Student Profile

-   **`POST /student/profile/create/`**
    -   **Description:** Create a student profile for the currently authenticated user.
    -   **Permissions:** IsAuthenticated
    -   **Request Body:**
        ```json
        {
            "language": "EN",
            "current_grade": "GR10"
        }
        ```
    -   **Response:**
        ```json
        {
            "language": "EN",
            "current_grade": "GR10"
        }
        ```

-   **`GET /student/profile/`**
    -   **Description:** Retrieve the student profile for the currently authenticated user.
    -   **Permissions:** IsAuthenticated
    -   **Response:**
        ```json
        {
            "id": 1,
            "username": "student_username",
            "email": "student@example.com",
            "first_name": "Student",
            "last_name": "User",
            "language": "EN",
            "current_grade": "GR10"
        }
        ```

-   **`PUT /student/profile/`**
    -   **Description:** Update the student profile for the currently authenticated user.
    -   **Permissions:** IsAuthenticated
    -   **Request Body:**
        ```json
        {
            "language": "FR",
            "current_grade": "GR11"
        }
        ```
    -   **Response:** (Same as `GET /student/profile/`)

-   **`PATCH /student/profile/`**
    -   **Description:** Partially update the student profile for the currently authenticated user.
    -   **Permissions:** IsAuthenticated
    -   **Request Body:** (Partial data from `PUT /student/profile/`)
    -   **Response:** (Same as `GET /student/profile/`)

### Enrollments

-   **`GET /student/enrollments/`**
    -   **Description:** List the subjects a student is enrolled in.
    -   **Permissions:** IsAuthenticated
    -   **Response:**
        ```json
        [
            {
                "id": 1,
                "student": "student_username",
                "subject": "Mathematics",
                "enrolled_at": "..."
            }
        ]
        ```

### Quiz Submission

-   **`POST /quizzes/submit/`**
    -   **Description:** Submit answers for a quiz.
    -   **Permissions:** IsAuthenticated, IsEnrolledStudent
    -   **Request Body:**
        ```json
        {
            "quiz_id": 1,
            "responses": [
                {"question_id": 1, "answer": "A"},
                {"question_id": 2, "answer": "B"}
            ]
        }
        ```
    -   **Response:**
        ```json
        {
            "attempt": { ... },
            "ai_feedback": "...",
            "regenerated_quiz": { ... } // Optional
        }
        ```

### Quiz Attempts

-   **`GET /quiz-attempts/`**
    -   **Description:** Retrieve a list of quiz attempts for the current user (or all attempts for admins).
    -   **Permissions:** IsAuthenticated
    -   **Response:**
        ```json
        [
            {
                "id": 1,
                "student": { ... },
                "quiz": { ... },
                "start_time": "...",
                "end_time": "...",
                "score": 85.5,
                "passed": true,
                "cheating_detected": false
            }
        ]
        ```

-   **`GET /quiz-attempts/{attempt_id}/`**
    -   **Description:** Get detailed results of a quiz attempt.
    -   **Permissions:** IsAuthenticated, IsStudentOwner
    -   **Response:**
        ```json
        {
            "attempt": { ... },
            "responses": [ ... ]
        }
        ```

### Dashboards

-   **`GET /dashboard/student/`**
    -   **Description:** Get dashboard data for the current student.
    -   **Permissions:** IsAuthenticated
    -   **Response:**
        ```json
        {
            "student": { ... },
            "enrollments": [ ... ],
            "recent_attempts": [ ... ],
            "practice_tasks": [ ... ]
        }
        ```

-   **`GET /dashboard/admin/`**
    -   **Description:** Get dashboard data for an admin user.
    -   **Permissions:** IsStaffOrAdmin
    -   **Response:**
        ```json
        {
            "total_students": 100,
            "total_lessons": 50,
            "total_subjects": 10,
            "total_quizzes": 200,
            "recent_lessons": [ ... ],
            "recent_attempts": [ ... ]
        }
        ```

### AI Assistant

-   **`POST /ai/assist/`**
    -   **Description:** Provide the message and context and get assist by AI.
    -   **Permissions:** IsAuthenticated
    -  **Request Body:**
        ```json
        {
            "message":"",
            "context":""
        }
        ```
    -   **Response:**
        ```json
        {
            "response": ""
        }
        ```
