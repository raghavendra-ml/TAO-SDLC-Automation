@echo off
echo ========================================
echo Starting TAO SDLC Backend
echo ========================================
echo.

cd backend

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Installing/Updating dependencies...
pip install -r requirements.txt --quiet

echo.
echo ========================================
echo Backend starting at http://localhost:8000
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn app.main:app --reload

