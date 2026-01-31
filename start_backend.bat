@echo off
echo Stopping Docker Backend to free port 8000...
docker stop authorizationandrbac-backend-1

echo Setting up Environment Variables...
set DB_HOST=localhost
set DB_PORT=5432
set DB_USER=postgres
set DB_PASS=password
set DB_NAME=rbac_db
set JWT_SECRET=your_secret_key_here_change_in_production
set REDIS_URL=redis://localhost:6379/0

cd backend
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate
)
cd ..

echo Starting Local Backend on Port 8000...
echo Running from Project Root to support relative imports...
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

pause
