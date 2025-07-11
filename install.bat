@echo off
title ResumeMatch - Automated Installation
color 0A

echo.
echo ========================================
echo    ResumeMatch - Automated Installer
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [INFO] Python found. Checking version...
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.8+ is required
    echo Please upgrade your Python installation
    pause
    exit /b 1
)

echo [SUCCESS] Python version check passed
echo.

:: Create virtual environment
echo [INFO] Creating virtual environment...
if exist venv (
    echo [INFO] Virtual environment already exists, removing old one...
    rmdir /s /q venv
)

python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

echo [SUCCESS] Virtual environment created
echo.

:: Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

echo [SUCCESS] Virtual environment activated
echo.

:: Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip
echo.

:: Install requirements
echo [INFO] Installing Python dependencies...
echo This may take a few minutes...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo [SUCCESS] Dependencies installed successfully
echo.

:: Download NLTK data
echo [INFO] Downloading NLTK data...
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('punkt_tab', quiet=True); print('NLTK data downloaded successfully!')"
if errorlevel 1 (
    echo [WARNING] NLTK data download failed, but continuing...
)
echo.

:: Create necessary directories
echo [INFO] Creating application directories...
if not exist data mkdir data
if not exist uploads mkdir uploads
if not exist resumes mkdir resumes
if not exist job_descriptions mkdir job_descriptions
echo [SUCCESS] Directories created
echo.

:: Initialize application data
echo [INFO] Initializing application data...
python -c "
import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

# Create default data files
if not os.path.exists('data/users.json'):
    with open('data/users.json', 'w') as f:
        json.dump({}, f)

if not os.path.exists('data/jobs.json'):
    with open('data/jobs.json', 'w') as f:
        json.dump([], f)

if not os.path.exists('data/applications.json'):
    with open('data/applications.json', 'w') as f:
        json.dump([], f)

if not os.path.exists('data/logs.json'):
    with open('data/logs.json', 'w') as f:
        json.dump([], f)

# Create admin account
admin_data = {
    'admin': {
        'password': generate_password_hash('admin123'),
        'email': 'admin@resumematch.com',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'last_login': None,
        'is_active': True
    }
}
with open('data/admins.json', 'w') as f:
    json.dump(admin_data, f, indent=4)

print('Application data initialized successfully!')
"

echo.
echo ========================================
echo       Installation Complete!
echo ========================================
echo.
echo [SUCCESS] ResumeMatch has been installed successfully!
echo.
echo To start the application:
echo   1. Run: start_app.bat
echo   2. Or manually: venv\Scripts\activate.bat && python app.py
echo.
echo Default admin credentials:
echo   Username: admin
echo   Password: admin123
echo.
echo The application will be available at: http://localhost:5000
echo.
echo [IMPORTANT] Please change the default admin password after first login!
echo.

:: Create start script
echo [INFO] Creating startup script...
echo @echo off > start_app.bat
echo title ResumeMatch Application >> start_app.bat
echo call venv\Scripts\activate.bat >> start_app.bat
echo echo Starting ResumeMatch... >> start_app.bat
echo echo Application will be available at: http://localhost:5000 >> start_app.bat
echo echo Press Ctrl+C to stop the application >> start_app.bat
echo python app.py >> start_app.bat
echo pause >> start_app.bat

echo [SUCCESS] Startup script created: start_app.bat
echo.

pause
