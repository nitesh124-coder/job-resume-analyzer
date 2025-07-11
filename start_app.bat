@echo off
title ResumeMatch Application
color 0A

echo.
echo ========================================
echo       ResumeMatch Application
echo ========================================
echo.

:: Check if virtual environment exists
if not exist "venv" (
    echo [ERROR] Virtual environment not found!
    echo Please run install.bat first to set up the application.
    echo.
    pause
    exit /b 1
)

:: Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    echo Please run install.bat to reinstall the application.
    pause
    exit /b 1
)

echo [SUCCESS] Virtual environment activated
echo.

:: Check if required files exist
if not exist "app.py" (
    echo [ERROR] app.py not found!
    echo Please ensure you're in the correct directory.
    pause
    exit /b 1
)

if not exist "data" (
    echo [WARNING] Data directory not found, creating...
    mkdir data
)

:: Start the application
echo [INFO] Starting ResumeMatch application...
echo.
echo ========================================
echo   Application Starting...
echo ========================================
echo.
echo The application will be available at:
echo   http://localhost:5000
echo.
echo Default admin credentials:
echo   Username: admin
echo   Password: admin123
echo.
echo Press Ctrl+C to stop the application
echo ========================================
echo.

:: Run the Flask application
python app.py

:: If we get here, the application has stopped
echo.
echo ========================================
echo   Application Stopped
echo ========================================
echo.
pause
