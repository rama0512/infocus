# AGENTS.md

## Workspace Architecture
- Frontend: Vue.js 3 (using Vite, Vue Router)
- Backend API: FastAPI (Python 3.11+, Pydantic v2)
- ML Layer: OpenCV, NumPy, Python (Asynchronous integration)

## Core Commands
- Frontend Run: `npm run dev` inside /frontend
- Backend Run: `uvicorn main:app --reload` inside /backend

## Engineering Standards

### 1. Frontend (Vue.js + Vite)


### 2. Backend (FastAPI)
- **Typing**: Enforce strict Python type hinting.
- **Data Validation**: Utilize Pydantic v2 BaseModels for all request and response payloads.
- **Async Execution**: Define API endpoints using `async def` unless interacting with a blocking third-party package.
- **Dependency Injection**: Leverage FastAPI's `Depends` system for database sessions, security, and ML model sharing.

### 3. ML Layer (Python + OpenCV)
- **Memory Management**: Explicitly release references to large OpenCV image matrices (`cv2.Mat`) when finished.

## Boundaries & Constraints
- Never modify database migration scripts (`/migrations` or `alembic`) without strict manual confirmation.
- Do not add heavy deep learning packages (like PyTorch or TensorFlow) unless explicitly instructed.
- Do not mix frontend Vite configuration modifications into backend API change requests.
