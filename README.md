# FastAPI Calculator with Secure User Auth API & Calculation Models

A production-ready FastAPI application featuring a fully functional interactive calculator and a secure user authentication system backed by PostgreSQL. The project includes automated CI/CD pipelines, comprehensive testing, and containerization.

## Features

* **Calculator API & History:** Endpoints for addition, subtraction, multiplication, and division, with all operations securely saved to the database using a structured `Calculation` model.
* **Robust Data Validation:** Strict input validation utilizing Pydantic schemas to catch errors (like division by zero or invalid data types) before they ever reach the database or business logic.
* **Scalable Architecture:** Implements the Factory Design Pattern to cleanly decouple the mathematical calculation logic from the API routing and database layers.
* **Interactive Frontend:** A clean, HTML/JS frontend to interact with the calculator endpoints.
* **Secure User Management:** User registration with secure password hashing using `passlib` and `bcrypt`, with foreign-key relationships linking users to their calculation history.
* **PostgreSQL Integration:** Fully integrated relational database setup using SQLAlchemy ORM.
* **Comprehensive Testing:** Unit, integration, and End-to-End (E2E) testing using `pytest` and `playwright`.
* **Automated CI/CD:** GitHub Actions pipeline configured for testing, security scanning (Bandit), and automated deployment to Docker Hub.

---

## Prerequisites

Before you begin, ensure you have the following installed on your machine:
* **Python 3.11+**
* **Docker Desktop** (for running the local PostgreSQL database)
* **Git**

---

## Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Aniket-NJIT/module_10_database_testing.git
cd module_10_database_testing
```
### 2. Set Up a Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
playwright install chromium  # Required for E2E UI testing
```

### 4. Start the Database (Docker Compose)
```bash
docker compose up -d
```
Access pgAdmin at http://localhost:5050 (Login: `admin@admin.com` / Password: admin).

Once connected to pgAdmin, create two databases:
1. calculator_db (For the main application)
2. test_calculator_db (For local testing)


### 5. Run the Application
```bash
uvicorn main:app --reload
```
- Frontend UI: http://127.0.0.1:8000/
- Interactive API Docs (Swagger): http://127.0.0.1:8000/docs

### 6. Run Tests Locally
```bash
pytest
```
The test suite covers:

- test_main.py: Validates API route responses and basic Pydantic schema validation for incoming requests.

- test_operations.py: Unit tests for the core mathematical functions.

- test_users.py: Integration tests for user creation, database constraints (duplicate emails), and secure password hashing.

- test_calculations.py: Unit and integration tests validating the Calculation model, the factory pattern logic, and strict Pydantic schema validations (e.g., explicitly preventing division by zero at the schema level).

- test_e2e.py: End-to-End Playwright tests that spin up a headless browser to click through the frontend UI and verify visual outputs.

### Docker Hub & Deployment
This project is fully containerized and automatically built and pushed to Docker Hub upon every successful merge to the main branch via GitHub Actions.

View the docker hub repository at: https://hub.docker.com/r/akhalate/fastapi-calculation-model

You can pull the latest built image directly from Docker Hub to run the application anywhere:
```bash
docker pull akhalate/fastapi-calculation-model
```

To run the containerized application locally (Note: You must pass in your database credentials):
```bash
docker run -p 8000:8000 -e DATABASE_URL="postgresql://postgres:postgres@host.docker.internal:5432/calculator_db" akhalate/fastapi-calculation-model:latest
```

### CI/CD Pipeline Architecture
The `.github/workflows/ci-cd.yml` file dictates the automated workflow:
1. Test Job: Spins up a fresh PostgreSQL service container, installs dependencies, and runs the full pytest suite.
2. Security Job: Runs bandit to scan the codebase for known vulnerabilities.
3. Deploy Job: Authenticates with Docker Hub and pushes the newly built image, tagged as latest.