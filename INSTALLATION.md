# ResumeMatch Installation Guide

This comprehensive guide will help you install and set up ResumeMatch on Windows.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Installation](#quick-installation)
- [Manual Installation](#manual-installation)
- [Development Setup](#development-setup)
- [Troubleshooting](#troubleshooting)
- [Post-Installation](#post-installation)

## Prerequisites

### System Requirements
- **Operating System**: Windows 10 or higher
- **Python**: Version 3.8 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: At least 1GB free space
- **Internet**: Required for initial setup and dependency installation

### Required Software
1. **Python 3.8+**: Download from [python.org](https://www.python.org/downloads/)
2. **Git**: Download from [git-scm.com](https://git-scm.com/downloads)
3. **pip**: Usually comes with Python installation

### Optional Software
- **Visual Studio Code**: Recommended IDE
- **Postman**: For API testing (future features)

## Quick Installation

```batch
# 1. Clone the repository
git clone https://github.com/your-username/ResumeMatch.git
cd ResumeMatch

# 2. Run the automated installer
install.bat
```

## Manual Installation

### Step 1: Clone Repository
```batch
git clone https://github.com/your-username/ResumeMatch.git
cd ResumeMatch
```

### Step 2: Create Virtual Environment
```batch
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

### Step 3: Install Dependencies
```batch
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### Step 4: Download NLTK Data
```batch
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab'); print('NLTK data downloaded successfully!')"
```

### Step 5: Initialize Application
```batch
# Create directories
mkdir data uploads resumes job_descriptions

# Initialize data files
python -c "import json; import os; from datetime import datetime; from werkzeug.security import generate_password_hash; files = ['users.json', 'jobs.json', 'applications.json', 'logs.json']; [open(f'data/{file}', 'w').write(json.dumps([] if file != 'users.json' else {})) for file in files if not os.path.exists(f'data/{file}')]; admin_data = {'admin': {'password': generate_password_hash('admin123'), 'email': 'admin@resumematch.com', 'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'last_login': None, 'is_active': True}}; open('data/admins.json', 'w').write(json.dumps(admin_data, indent=4)); print('Application initialized successfully!')"
```

### Step 6: Start Application
```batch
python app.py
```



## Development Setup

### Additional Dependencies
```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-flask pytest-cov black flake8 mypy
```

### Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
# Set FLASK_ENV=development for development mode
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_app.py
```

### Code Formatting
```bash
# Format code with black
black .

# Check code style with flake8
flake8 .

# Type checking with mypy
mypy app.py
```

## Troubleshooting

### Common Issues

#### Python Not Found
**Error**: `'python' is not recognized as an internal or external command`

**Solution**:
- Ensure Python is installed
- Add Python to system PATH
- Try using `python3` instead of `python`



#### NLTK Data Download Fails
**Error**: `Resource punkt not found`

**Solution**:
```python
import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt')
nltk.download('stopwords')
```

#### Port Already in Use
**Error**: `Address already in use`

**Solution**:
```batch
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process or use different port
taskkill /PID <process_id> /F
```

#### Virtual Environment Issues
**Error**: Various virtual environment related errors

**Solution**:
```batch
# Remove and recreate virtual environment
rmdir /s venv

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
```

#### Import Errors
**Error**: `ModuleNotFoundError: No module named 'flask'`

**Solution**:
```batch
# Ensure virtual environment is activated
venv\Scripts\activate

# Reinstall requirements
pip install -r requirements.txt
```

### Getting Help

If you encounter issues not covered here:

1. Check the [Issues](https://github.com/your-username/ResumeMatch/issues) page
2. Search for existing solutions
3. Create a new issue with:
   - Operating system and version
   - Python version
   - Error message (full traceback)
   - Steps to reproduce

## Post-Installation

### First Run Checklist
- [ ] Application starts without errors
- [ ] Web interface accessible at http://localhost:5000
- [ ] Admin login works (admin/admin123)
- [ ] File upload functionality works
- [ ] Resume analysis produces results

### Security Setup
1. **Change Default Admin Password**
   - Login as admin
   - Go to Admin Settings
   - Update password

2. **Configure Environment Variables**
   - Copy `.env.example` to `.env`
   - Update `SECRET_KEY` with a secure random string
   - Configure other settings as needed

3. **Set Up HTTPS** (Production)
   - Use a reverse proxy (nginx, Apache)
   - Configure SSL certificates
   - Update Flask configuration

### Performance Optimization
1. **Production Settings**
   - Set `FLASK_ENV=production`
   - Disable debug mode
   - Configure proper logging

2. **Resource Limits**
   - Adjust `MAX_CONTENT_LENGTH` for file uploads
   - Configure session timeout
   - Set up log rotation

### Backup Strategy
1. **Data Backup**
   - Regularly backup `data/` directory
   - Export user data and job postings
   - Save uploaded resumes

2. **Configuration Backup**
   - Save `.env` file securely
   - Document custom configurations
   - Version control settings

## Next Steps

After successful installation:

1. **Explore the Application**
   - Register a test user account
   - Upload a sample resume
   - Try the job matching features

2. **Customize for Your Needs**
   - Add your job descriptions
   - Configure skill categories
   - Customize the interface

3. **Set Up Monitoring**
   - Configure logging
   - Set up health checks
   - Monitor system resources

4. **Plan for Production**
   - Choose hosting platform
   - Set up CI/CD pipeline
   - Configure monitoring and alerts

---

**Congratulations!** ResumeMatch is now installed and ready to use. Visit http://localhost:5000 to get started!
