@echo off
echo ========================================
echo TAO SDLC Database Seed Script
echo ========================================
echo.

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found
    echo Please run start_backend.bat first to create the virtual environment
    pause
    exit /b 1
)

echo.
echo Running seed script...
echo.

python seed_database.py

echo.
echo ========================================
echo Seed script completed
echo ========================================
echo.
pause

