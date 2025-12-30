# Online Forum - Backend API

A fast, minimal, and modern community forum platform backend built with FastAPI and PostgreSQL.

## 🚀 Quick Start

### Prerequisites

- [Python 3.13+](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/)
- [uv](https://docs.astral.sh/uv/)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Abonsama/online-forum.git
   cd online-forum/backend
   ```

2. **Install dependencies**

   Create a virtual environment

   ```bash
   python -m venv .venv
   ```

   Activate the virtual environment

   ```bash
   # On Linux / macOS
   source .venv/bin/activate
   # On Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   ```

   Install dependencies

   ```bash
   # Install dependencies
   uv sync --all-groups

   # Install pre-commit hooks
   pre-commit install
   ```

   **Note:** If you are facing SSL issues on Windows, use:

   ```bash
   uv sync --all-groups --native-tls
   ```

3. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Configure database**

   ```bash
   # Create database
   createdb online_forum

   # Run migrations
   alembic upgrade head
   ```

5. **Start the development server**

   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/          # API routes and endpoints
│   ├── core/         # Core configurations
│   ├── models/       # SQLAlchemy models
│   ├── schemas/      # Pydantic schemas
│   └── services/     # Business logic
├── alembic/          # Database migrations
├── tests/            # Test suite
├── .env.example      # Environment variables template
├── main.py           # Application entry point
└── pyproject.toml    # Project dependencies
```

## 🛠️ Technology Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL with SQLAlchemy (async)
- **Migration:** Alembic
- **Authentication:** JWT with python-jose
- **Password Hashing:** Argon2 (pwdlib)
- **Validation:** Pydantic & email-validator
- **ASGI Server:** Uvicorn with uvloop (Linux)
- **Logging:** Loguru

## 🔧 Development

### Running Tests

```bash
pytest
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Quality

```bash
# Run pre-commit hooks
pre-commit run --all-files

# Format code
ruff format .

# Lint code
ruff check .
```

## 📚 API Documentation

Once the server is running, visit:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## 🔐 Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/online_forum

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
DEBUG=True
ENVIRONMENT=development
```

## 🚢 Production Deployment

```bash
# Using Gunicorn with Uvicorn workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📄 License

[Add your license here]

## 👥 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Contact

For questions or support, please open an issue on GitHub.
