# ResumeMatch - AI-Powered Resume Analysis System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

ResumeMatch is an intelligent resume analysis system that uses advanced Natural Language Processing (NLP) and Machine Learning techniques to match resumes with job descriptions. The system provides comprehensive skill analysis, job matching, and detailed insights to help job seekers find the best opportunities.

## 🚀 Features

### Core Functionality
- **Multi-format Document Support**: PDF, DOCX, DOC, and TXT files
- **Advanced Text Extraction**: Robust document processing with fallback mechanisms
- **Intelligent Skill Detection**: Comprehensive skill extraction and categorization
- **Job Matching Algorithm**: TF-IDF based similarity scoring with enhanced analytics
- **Interactive Web Interface**: Modern, responsive web application
- **User Management**: Secure user registration and authentication
- **Admin Dashboard**: Complete administrative control panel

### Enhanced Analytics
- **Skill Gap Analysis**: Identify missing skills for target positions
- **Category-wise Matching**: Detailed breakdown by skill categories
- **Visual Results**: Interactive charts and detailed match reports
- **Job Recommendations**: Top job matches with similarity scores
- **Resume Management**: Upload and manage multiple resumes

### Administrative Features
- **User Management**: View and manage all registered users
- **Job Management**: Add, edit, and organize job postings
- **Application Tracking**: Monitor job applications and user activity
- **System Logs**: Comprehensive logging and monitoring
- **Analytics Dashboard**: System statistics and insights

## 🔧 Technology Stack

- **Backend**: Python 3.8+, Flask 2.3.3
- **NLP**: NLTK 3.8.1, scikit-learn 1.3.2
- **Document Processing**: PyPDF2, python-docx, pdfplumber
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap
- **Database**: JSON-based file storage
- **Security**: Werkzeug password hashing, secure sessions

## 📋 Requirements

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows 10 or higher
- **Memory**: Minimum 4GB RAM recommended
- **Storage**: At least 1GB free space

### Python Dependencies
All dependencies are listed in `requirements.txt` with specific versions for compatibility.

## 🛠️ Installation

### Quick Start (Recommended)

```batch
# Clone the repository
https://github.com/nitesh124-coder/job-resume-analyzer
cd ResumeMatch

# Run the automated installer
install.bat
```

### Manual Installation

#### 1. Clone the Repository
```batch
https://github.com/nitesh124-coder/job-resume-analyzer
cd ResumeMatch
```

#### 2. Create Virtual Environment (Recommended)
```batch
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

#### 3. Install Dependencies
```batch
# Install all required packages
pip install -r requirements.txt
```

#### 4. Download NLTK Data
```batch
# Run this Python script to download required NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab'); print('NLTK data downloaded successfully!')"
```

#### 5. Initialize the Application
```batch
# Create necessary directories and initialize data
python -c "import os; os.makedirs('data', exist_ok=True); os.makedirs('uploads', exist_ok=True); os.makedirs('resumes', exist_ok=True); print('Application initialized successfully!')"
```

## 🚀 Usage

### Starting the Application

#### Web Application (Recommended)
```batch
# Start the Flask web server using the startup script
start_app.bat

# Or manually:
python app.py
```
Then open your browser and navigate to: `http://localhost:5000`

#### Command Line Interface
```batch
# For simple resume analysis
python runner.py
```

### Default Admin Credentials
- **Username**: `admin`
- **Password**: `admin123`

**⚠️ Important**: Change the default admin password after first login!

## 📁 Project Structure

```
ResumeMatch/
├── app.py                 # Main Flask application
├── document_processor.py  # Document text extraction
├── skill_extractor.py    # Advanced skill detection
├── runner.py             # CLI interface
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── data/                # Application data
│   ├── users.json       # User accounts
│   ├── jobs.json        # Job postings
│   ├── admins.json      # Admin accounts
│   ├── applications.json # Job applications
│   └── logs.json        # System logs
├── templates/           # HTML templates
├── static/             # CSS, JS, images
├── uploads/            # User uploaded files
├── resumes/            # Resume storage
├── job_descriptions/   # Job description files
└── jobs/              # Sample job files
```

## 🎯 How It Works

### TF-IDF Algorithm
ResumeMatch uses **TF-IDF (Term Frequency-Inverse Document Frequency)** for document similarity analysis:

- **Term Frequency (TF)**: Measures how often a word appears in a document
- **Inverse Document Frequency (IDF)**: Measures how rare a word is across all documents
- **Combined Score**: Emphasizes important, document-specific words while filtering common words

### Benefits of TF-IDF:
1. **Highlighting Important Words**: Emphasizes relevant, specific terms
2. **Feature Extraction**: Converts text to numerical features for ML algorithms
3. **Dimensionality Reduction**: Reduces complexity while retaining crucial information
4. **Noise Filtering**: Removes common stopwords and focuses on meaningful content
5. **Length Independence**: Doesn't favor longer documents unfairly

### Enhanced Skill Extraction
The system uses multiple methods for comprehensive skill detection:
- **Direct Keyword Matching**: Exact skill name recognition
- **Pattern-based Extraction**: Context-aware skill identification
- **Category Classification**: Groups skills into relevant categories
- **Experience Level Detection**: Identifies years of experience with technologies

## 📊 Features in Detail

### Resume Analysis
- Upload resumes in multiple formats (PDF, DOCX, DOC, TXT)
- Extract and analyze skills across 10+ categories
- Generate detailed skill profiles
- Compare against job requirements

### Job Matching
- Calculate similarity scores using advanced NLP
- Provide category-wise match analysis
- Suggest skill improvements
- Rank job opportunities by compatibility

### Admin Dashboard
- Monitor system usage and performance
- Manage users and job postings
- View application statistics
- Access comprehensive logs

## 🔒 Security Features

- **Password Hashing**: Secure password storage using Werkzeug
- **Session Management**: Secure user sessions with timeout
- **File Upload Security**: Validated file types and secure filename handling
- **Admin Access Control**: Separate admin authentication system
- **Input Validation**: Comprehensive input sanitization

## 🧪 Testing

Run the test suite:
```bash
# Install testing dependencies
pip install pytest pytest-flask pytest-cov

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html
```
