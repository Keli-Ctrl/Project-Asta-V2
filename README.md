# Project Asta

Institutional-grade AI-assisted automated trading infrastructure.

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)

### Setup
1. Clone the repository.
2. Copy `.env.example` to `.env` and fill in your API keys.
3. Run with Docker Compose:
   ```bash
   docker-compose -f docker/docker-compose.yml up --build
   ```

### Project Structure
- `src/asta_brain`: Central Python backend (FastAPI).
- `src/dashboard`: React frontend.
- `docker/`: Docker configuration files.

## Development
To run the backend locally:
1. Create a virtual environment: `python -m venv venv`
2. Activate it: `source venv/bin/activate` (Linux/macOS)
3. Install dependencies: `pip install -e ".[dev]"`
4. Run the app: `uvicorn src.asta_brain.main:app --reload`

## License
Proprietary
