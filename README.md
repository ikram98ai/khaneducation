# Khan Education API 🚀

**An intelligent, scalable, and AI-driven backend for a next-generation personalized learning platform.**

## ✨ Vision

To democratize and revolutionize education by leveraging artificial intelligence to create personalized, engaging, and high-quality learning experiences that adapt to every user's unique needs.

---

## 🎯 Key Features

*   **🤖 AI-Powered Content Generation**: Dynamically creates comprehensive lessons and quizzes on any subject, transforming simple prompts into rich educational content.
*   **🎥 Automated Video Lessons**: Goes beyond text by generating complete video lessons, including scripts and voiceovers, to provide a multi-modal learning experience.
*   **scalable & Robust Backend**: Built with **FastAPI** and a modern technology stack, ensuring high performance, reliability, and developer efficiency.
*   **👤 Comprehensive User Management**: Full system for managing user profiles, tracking subject enrollment, and monitoring learning progress.
*   **☁️ Automated Cloud Deployment**: Infrastructure managed with **Terraform** and a complete **CI/CD pipeline** using GitHub Actions for automated, reliable deployments.

---

## 🎨 System Design

The system is designed for scalability, maintainability, and high performance, following modern software architecture principles.

### System Architecture
*Illustrates the decoupled, service-oriented architecture.*
![System Architecture](./assets/arch.png)

### AI Content Generation Flow
*Details the pipeline from prompt to generated text and video content.*
![AI Content Generation Flow](./assets/aiflow.png)

### Entity-Relationship Diagram (ERD)
*Defines the database schema and relationships between data entities.*
![Entity-Relationship Diagram](./assets/erd.png)

---

## 🛠️ Technical Deep-Dive

### Technology Stack

| Category      | Technology                               |
|---------------|------------------------------------------|
| **Backend**       | Python, FastAPI, Pydantic, Pynamodb   |
| **[Fronend](https://github.com/ikram98ai/khaneducation-web.git)**     | Typescript, React, TanStack Query, Zustand   |
| **Database**      | Dynamodb                               |
| **AI**            | Generative AI Models (Text & Video)      |
| **DevOps**        | Docker, Terraform, GitHub Actions        |
| **Tooling**       | `uv` for package management              |

### Architectural Overview

The API follows a clean, layered architecture to separate concerns and enhance maintainability:

-   **Routers**: (`/app/routers`) Defines the API endpoints, handles request validation, and forwards requests to the appropriate service layer.
-   **Services**: (`/app/services`) Contains the core business logic. It orchestrates operations between the database and other components, like the AI services.
-   **CRUD**: (`/app/crud`) An abstraction layer that handles all Create, Read, Update, and Delete database operations, making the services cleaner and more focused.
-   **Models & Schemas**: (`/app/models.py`, `/app/schemas.py`) Defines the database schema (Pynamodb models) and the API data structures (Pydantic schemas) for robust data validation and serialization.
-   **AI Engine**: (`/app/ai`) A dedicated module for all AI-related tasks, including prompt engineering and interfacing with generative models for content and video creation.

---

## 🚀 Getting Started

### Prerequisites

-   Python 3.11+
-   [Docker](https://www.docker.com/)
-   `uv` (recommended for package management)

### Local Development Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ikram98ai/khaneducation-api.git
    cd khaneducation-api
    ```

2.  **Set up environment variables:**
    *   Copy the example environment file and fill in the required values (e.g., database credentials, API keys).
    ```bash
    cp .env.example .env
    ```

3.  **Install dependencies:**
    ```bash
    uv pip install -r requirements.txt
    ```

4.  **Run the application with Uvicorn:**
    ```bash
    uvicorn app.main:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`.

5.  **Seed the database (optional):**
    *   To populate the database with initial data for testing:
    ```bash
    python seed_db.py
    ```

---

## 📚 API Documentation

Once the application is running, interactive API documentation (provided by Swagger UI) is automatically generated and available at:

`http://127.0.0.1:8000/docs`