# Khan Education API Documentation

This document provides comprehensive documentation for the Khan Education API, designed for seamless integration with the React web application.

## Application Overview

The Khan Education API is the backend service for a dynamic educational platform, designed to provide personalized learning experiences. This application leverages modern cloud technologies and artificial intelligence to deliver adaptive content and track student progress efficiently.

**Core Purpose & Value Proposition:**

*   **Personalized Learning**: Delivers tailored educational content (lessons, practice tasks, quizzes) based on student's grade level, language, and progress.
*   **AI-Powered Content Generation**: Utilizes AI to dynamically create and adapt learning materials, reducing manual content creation efforts and ensuring relevance.
*   **Progress Tracking & Analytics**: Provides comprehensive dashboards for students to monitor their learning journey, including completed lessons, quiz scores, and learning streaks.
*   **Scalable & Resilient Infrastructure**: Built on a serverless architecture, ensuring high availability, automatic scaling, and cost-effectiveness.

**Key Features:**

*   **User Management**: Secure authentication and management of student and instructor profiles.
*   **Subject & Lesson Management**: Organization and delivery of educational subjects and their associated lessons.
*   **Interactive Quizzes & Practice Tasks**: AI-generated assessments and exercises to reinforce learning, with automated feedback.
*   **Student Dashboards**: Real-time insights into student performance and engagement.

**Technical Architecture Highlights:**

*   **Backend Framework**: Developed using Python with FastAPI, known for its high performance and ease of use.
*   **Database**: Leverages Amazon DynamoDB (NoSQL) for flexible and scalable data storage, optimized for high-throughput, low-latency access.
*   **AI Integration**: Seamlessly integrates with AI services (e.g., Google Gemini API) for content generation and intelligent feedback.
*   **Serverless Deployment**: Deployed on AWS Lambda as containerized functions, managed by API Gateway for robust API exposure.
*   **Infrastructure as Code (IaC)**: Utilizes Terraform for defining and provisioning all cloud infrastructure, ensuring consistency, repeatability, and version control of the environment.
*   **Containerization**: Application is containerized using Docker, providing environment consistency from development to production.

## Base URL

The base URL for the API is `http://localhost:8000`.

## Authentication

The API uses JSON Web Tokens (JWT) for authentication. To access protected endpoints, you must first obtain an `access_token` by sending a `POST` request to the `/login` endpoint with your user credentials.

Once you have the `access_token`, include it in the `Authorization` header of all subsequent requests in the format:

```
Authorization: Bearer <your_access_token>
```

## API Endpoints

This section details all available API endpoints, their functionalities, expected inputs, and outputs.

### Authentication Routes (`/auth`)

*   **POST /login**
    *   **Description**: Authenticates a user and returns a JWT access token.
    *   **Input**: `schemas.UserLogin` (request body)
        ```json
        {
            "email": "user@example.com",
            "password": "your_password"
        }
        ```
    *   **Output**: `schemas.Token`
        ```json
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
        ```

### Subject Routes (`/subjects`)

*   **GET /subjects/**
    *   **Description**: Retrieves a list of all subjects.
    *   **Input**:
        *   `limit` (query parameter, optional): Maximum number of subjects to return (default: 100).
    *   **Output**: `List[schemas.Subject]`

*   **GET /subjects/{subject_id}/**
    *   **Description**: Retrieves details for a specific subject by its ID.
    *   **Input**:
        *   `subject_id` (path parameter, required): The unique identifier of the subject.
    *   **Output**: `schemas.SubjectDetail`

*   **GET /subjects/{subject_id}/details/**
    *   **Description**: Retrieves detailed information about a subject, including associated lessons, for the current student.
    *   **Input**:
        *   `subject_id` (path parameter, required): The unique identifier of the subject.
        *   `current_student` (dependency): Authenticated student object.
    *   **Output**: `schemas.SubjectDetail`

### Dashboard Routes (`/dashboard`)

*   **GET /dashboard/student/**
    *   **Description**: Retrieves dashboard statistics and enrolled subjects for the current student.
    *   **Input**:
        *   `current_student` (dependency): Authenticated student object.
    *   **Output**: `schemas.StudentDashboard`

### Lesson Routes (`/lessons`)

*   **GET /lessons/{lesson_id}/**
    *   **Description**: Retrieves details for a specific lesson by its ID.
    *   **Input**:
        *   `lesson_id` (path parameter, required): The unique identifier of the lesson.
    *   **Output**: `schemas.Lesson`

*   **GET /lessons/{lesson_id}/tasks/**
    *   **Description**: Retrieves practice tasks associated with a specific lesson.
    *   **Input**:
        *   `lesson_id` (path parameter, required): The unique identifier of the lesson.
    *   **Output**: `List[schemas.PracticeTask]`

*   **GET /lessons/{lesson_id}/quiz/**
    *   **Description**: Generates and retrieves a quiz for a specific lesson.
    *   **Input**:
        *   `lesson_id` (path parameter, required): The unique identifier of the lesson.
        *   `student` (dependency): Authenticated student object.
    *   **Output**: `schemas.Quiz`

*   **GET /lessons/{lesson_id}/attempts/**
    *   **Description**: Retrieves all quiz attempts for a specific lesson by the current student.
    *   **Input**:
        *   `lesson_id` (path parameter, required): The unique identifier of the lesson.
        *   `student` (dependency): Authenticated student object.
    *   **Output**: `List[schemas.QuizAttemptOut]`

### Quiz Routes (`/quizzes`)

*   **POST /quizzes/{quiz_id}/submit**
    *   **Description**: Submits responses for a quiz attempt.
    *   **Input**:
        *   `quiz_id` (path parameter, required): The unique identifier of the quiz.
        *   `responses` (request body): A list of student responses to quiz questions.
            ```json
            [
                {
                    "question_id": "string",
                    "student_answer": "string",
                    "is_correct": false
                }
            ]
            ```
        *   `current_student` (dependency): Authenticated student object.
    *   **Output**: `schemas.QuizSubmissionResponse`

### User Profile Routes (`/users`)

*   **GET /users/{id}/**
    *   **Description**: Retrieves user details by user ID.
    *   **Input**:
        *   `id` (path parameter, required): The unique identifier of the user.
    *   **Output**: `schemas.User`

*   **POST /users/**
    *   **Description**: Creates a new user.
    *   **Input**: `schemas.UserCreate` (request body)
        ```json
        {
            "username": "string",
            "first_name": "string",
            "last_name": "string",
            "role": "STUDENT",
            "email": "user@example.com",
            "password": "string"
        }
        ```
    *   **Output**: `schemas.User`

*   **GET /users/profile/me/**
    *   **Description**: Retrieves the profile of the currently authenticated user.
    *   **Input**:
        *   `user` (dependency): Authenticated user object.
    *   **Output**: `schemas.StudentProfile`

*   **POST /users/profile/me/**
    *   **Description**: Creates a student profile for the currently authenticated user.
    *   **Input**: `schemas.StudentCreate` (request body)
        ```json
        {
            "language": "EN",
            "current_grade": 1
        }
        ```
        *   `user` (dependency): Authenticated user object.
    *   **Output**: `schemas.StudentProfile`

*   **PUT /users/profile/me/**
    *   **Description**: Updates the details of the currently authenticated user.
    *   **Input**: `schemas.UserUpdate` (request body)
        ```json
        {
            "username": "string",
            "first_name": "string",
            "last_name": "string",
            "role": "STUDENT",
            "email": "user@example.com",
            "password": "string"
        }
        ```
        *   `current_user` (dependency): Authenticated user object.
    *   **Output**: `schemas.User`

*   **PUT /users/profile/me/student**
    *   **Description**: Updates the student-specific profile details for the currently authenticated user.
    *   **Input**: `schemas.StudentUpdate` (request body)
        ```json
        {
            "language": "EN",
            "current_grade": 1
        }
        ```
        *   `current_user` (dependency): Authenticated user object.
    *   **Output**: `schemas.Student`

