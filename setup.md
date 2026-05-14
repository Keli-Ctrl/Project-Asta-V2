# Local Deployment Guide: Project Asta

This guide provides step-by-step instructions for deploying Project Asta on a local machine for testing or development.

## 1. Prerequisites

Before starting, ensure you have the following installed:
- **Docker & Docker Compose**: (Recommended for easiest setup)
- **Python 3.11+**: (Required for manual/local development)
- **Node.js 18+ & npm**: (Required for manual frontend development)
- **MetaApi Token**: Obtain from [MetaApi.cloud](https://metaapi.cloud/)
- **Gemini API Key**: Obtain from [Google AI Studio](https://aistudio.google.com/) (for AI Reasoning Layer)

---

## 2. Environment Configuration

1. Clone the repository and navigate to the project root.
2. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
3. Open `.env` and configure the following variables:
   - `METAAPI_TOKEN`: Your MetaApi cloud token.
   - `GEMINI_API_KEY`: Your Gemini API key.
   - `DATABASE_URL`: If running locally, set to `postgresql+asyncpg://user:pass@localhost:5432/asta`.
   - `REDIS_URL`: If running locally, set to `redis://localhost:6379/0`.

---

## 3. Option A: Docker Deployment (Recommended)

Docker Compose handles the backend, frontend, database (PostgreSQL + TimescaleDB), and Redis automatically.

1. **Build and start the containers**:
   ```bash
   docker-compose -f docker/docker-compose.yml up --build
   ```
2. **Access the services**:
   - **Trading Brain (Backend)**: `http://localhost:8000`
   - **Dashboard (Frontend)**: `http://localhost:5173`
   - **PostgreSQL**: `localhost:5432`
   - **Redis**: `localhost:6379`

---

## 4. Option B: Manual Local Deployment (Development)

### Backend Setup
1. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```
3. **Run the FastAPI server**:
   ```bash
   uvicorn src.asta_brain.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup
1. **Navigate to the dashboard directory**:
   ```bash
   cd src/dashboard
   ```
2. **Install Node dependencies**:
   ```bash
   npm install
   ```
3. **Start the Vite development server**:
   ```bash
   npm run dev
   ```

---

## 5. Initializing the Database (Alembic)

Regardless of the deployment method, you must run the database migrations to create the required tables.

1. **Ensure the database is running** (either via Docker or a local PostgreSQL instance).
2. **Run migrations**:
   ```bash
   alembic upgrade head
   ```

---

## 6. Verifying the Setup

1. **Health Check**: Visit `http://localhost:8000/health`. You should receive a JSON response with `"status": "healthy"`.
2. **Dashboard**: Visit `http://localhost:5173`. You should see the Asta Terminal login/dashboard.
3. **Integration Demo**: To verify the entire stack is working (including AI and Risk engines), run:
   ```bash
   python src/shared/integration_demo.py
   ```

## 7. Troubleshooting

- **MetaApi Connectivity**: Ensure your `METAAPI_TOKEN` is valid and the account ID used in strategies is correctly provisioned in your MetaApi dashboard.
- **Database Connection**: If running manual deployment, ensure PostgreSQL is running and the user/password in `.env` match your local setup.
- **AI Layer**: If the AI Reasoning Layer fails, check your `GEMINI_API_KEY`. The system will fallback to a confidence multiplier of 0.5 if the AI layer is disabled.
