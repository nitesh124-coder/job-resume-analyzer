from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import os
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import json
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import datetime
from flask_login import login_required, current_user
from collections import Counter
import re
import logging
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our enhanced document processing modules
try:
    from document_processor import document_processor
    from skill_extractor import skill_extractor
    ENHANCED_PROCESSING_AVAILABLE = True
    logger.info("Enhanced document processing modules loaded successfully")
except ImportError as e:
    logger.warning(f"Enhanced processing modules not available: {e}")
    ENHANCED_PROCESSING_AVAILABLE = False

app = Flask(__name__)
# Use a fixed secret key for production, or load from environment variable
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=24)  # Session timeout
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc', 'docx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Initialize data directories with error handling
try:
    if not os.path.exists('data'):
        os.makedirs('data')

    if not os.path.exists('data/users.json'):
        with open('data/users.json', 'w') as f:
            json.dump({}, f)

    if not os.path.exists('data/jobs.json'):
        with open('data/jobs.json', 'w') as f:
            json.dump([], f)

    # Always recreate admin file to ensure correct password hash
    default_admin = {
        "admin": {
            "password": generate_password_hash("admin123"),
            "email": "admin@resumematch.com",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": None,
            "is_active": True
        }
    }
    with open('data/admins.json', 'w') as f:
        json.dump(default_admin, f, indent=4)

    if not os.path.exists('data/applications.json'):
        with open('data/applications.json', 'w') as f:
            json.dump([], f)

    if not os.path.exists('data/logs.json'):
        with open('data/logs.json', 'w') as f:
            json.dump([], f)
except Exception as e:
    logger.error(f"Error initializing data directories: {str(e)}")
    raise

# Create job description files
job_desc_dir = "job_descriptions"
if not os.path.exists(job_desc_dir):
    os.makedirs(job_desc_dir)

    # Load sample jobs
    with open('data/jobs.json', 'r') as f:
        jobs = json.load(f)

    # Create detailed job description files
    for job in jobs:
        job_id = job["id"]
        filename = os.path.join(job_desc_dir, f"{job_id}.txt")

        if not os.path.exists(filename):
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# {job['company']}\n\n")
                f.write(f"## {job['title']}\n\n")
                f.write(f"**Location:** {job['location']}\n")
                f.write(f"**Experience Required:** {job['experience']}\n")
                f.write(f"**Salary:** {job['salary']}\n\n")
                f.write(f"### Company Overview\n\n{job['description']}\n\n")
                f.write("### Job Description\n\nWe are looking for a talented and motivated professional to join our team. The ideal candidate will have a strong background in their field and excellent communication skills.\n\n")
                f.write("### Requirements\n\n- Relevant experience in the field\n- Strong problem-solving abilities\n- Excellent communication skills\n- Ability to work in a team environment\n- Knowledge of industry best practices\n\n")
                f.write("### Benefits\n\n- Competitive salary package\n- Health insurance\n- Professional development opportunities\n- Work-life balance\n- Collaborative work environment\n\n")
                f.write("### How to Apply\n\nSubmit your resume and cover letter through our career portal. Shortlisted candidates will be contacted for interviews.")

if not os.path.exists('uploads'):
    os.makedirs('uploads')

# From NLTK, provides common stopwords like 'An, The, Who ..'
stop_words = set(stopwords.words('english'))

# Filter out non-alphabetic tokens and stopwords
def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    tokens = [token for token in tokens if token.isalpha() and token not in stop_words]
    preprocessed_text = " ".join(tokens)
    return preprocessed_text

# This is for calculating the similarity of the job description & resume
def calculate_tfidf_similarity(file1_path, file2_path):
    try:
        # Try decoding resume with utf-8 first
        with open(file1_path, 'r', encoding='utf-8') as file1:
            file1_contents = file1.read()
    except UnicodeDecodeError:
        # If utf-8 fails, try decoding with latin-1 (common for some text files)
        try:
            with open(file1_path, 'r', encoding='latin-1') as file1:
                file1_contents = file1.read()
        except Exception as e:
            # If both fail, log the error and perhaps return a low similarity score or raise a specific error
            print(f"Error decoding resume file {file1_path}: {e}")
            return 0.0 # Return 0 similarity or handle as an error

    # Job description file should ideally be consistent, assuming utf-8
    try:
        with open(file2_path, 'r', encoding='utf-8') as file2:
            file2_contents = file2.read()
    except UnicodeDecodeError:
         # If utf-8 fails for job description, try decoding with latin-1
        try:
            with open(file2_path, 'r', encoding='latin-1') as file2:
                file2_contents = file2.read()
        except Exception as e:
             print(f"Error decoding job description file {file2_path}: {e}")
             return 0.0 # Return 0 similarity or handle as an error


    file1_preprocessed = preprocess_text(file1_contents)
    file2_preprocessed = preprocess_text(file2_contents)

    # If either file is empty after preprocessing, return 0 similarity
    if not file1_preprocessed or not file2_preprocessed:
        return 0.0

    # TF-IDF vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([file1_preprocessed, file2_preprocessed])

    # Get the TF-IDF vectors for file1 and file2
    file1_tfidf = tfidf_matrix[0]
    file2_tfidf = tfidf_matrix[1]

    # Calculate cosine similarity
    similarity = (file1_tfidf * file2_tfidf.T).toarray()[0, 0]

    return similarity

def calculate_enhanced_similarity(text1, text2):
    """
    Enhanced similarity calculation for extracted text
    """
    if not text1 or not text2:
        return 0.0

    try:
        # Preprocess both texts
        text1_processed = preprocess_text(text1)
        text2_processed = preprocess_text(text2)

        if not text1_processed or not text2_processed:
            return 0.0

        # Calculate TF-IDF similarity
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([text1_processed, text2_processed])

        similarity = (tfidf_matrix[0] * tfidf_matrix[1].T).toarray()[0, 0]
        return similarity

    except Exception as e:
        logger.error(f"Error calculating enhanced similarity: {str(e)}")
        return 0.0

def analyze_resume_fallback(resume_index):
    """
    Fallback analysis method using the old approach
    """
    users = get_users()
    user_data = users[session['username']]
    resume = user_data['resumes'][resume_index]
    file1_path = resume['path']

    # Analyze against job description files
    job_desc_dir = "job_descriptions"
    max_similarity = 0.0
    most_similar_file = None
    all_files = {}

    # Loop through job description files
    for filename in os.listdir(job_desc_dir):
        if filename.endswith('.txt'):
            file2_path = os.path.join(job_desc_dir, filename)
            similarity = calculate_tfidf_similarity(file1_path, file2_path)
            job_id = os.path.splitext(filename)[0]
            job = get_job_by_id(job_id)
            job_title = job['title'] if job else job_id

            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_file = job_title

            all_files[job_title] = similarity

    # Sort results
    all_files_sorted = sorted(all_files.items(), key=lambda x: x[1], reverse=True)
    top_five = all_files_sorted[:5]
    bottom_five = all_files_sorted[-5:][::-1]

    result = {
        'most_similar': {
            'job': most_similar_file,
            'similarity': max_similarity
        },
        'top_five': top_five,
        'bottom_five': bottom_five
    }

    return render_template('results.html', result=result, resume_name=resume['name'])

# User authentication helpers
def get_users():
    with open('data/users.json', 'r') as f:
        return json.load(f)

def save_users(users):
    with open('data/users.json', 'w') as f:
        json.dump(users, f, indent=4)

def user_exists(username):
    users = get_users()
    return username in users

# Admin authentication helpers
def get_admins():
    with open('data/admins.json', 'r') as f:
        return json.load(f)

def save_admins(admins):
    with open('data/admins.json', 'w') as f:
        json.dump(admins, f, indent=4)

def admin_exists(username):
    admins = get_admins()
    return username in admins

def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_username' not in session:
            flash('Please log in as admin to access this page.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Application helpers
def get_applications():
    with open('data/applications.json', 'r') as f:
        return json.load(f)

def save_applications(applications):
    with open('data/applications.json', 'w') as f:
        json.dump(applications, f, indent=4)

def get_logs():
    with open('data/logs.json', 'r') as f:
        return json.load(f)

def save_logs(logs):
    with open('data/logs.json', 'w') as f:
        json.dump(logs, f, indent=4)

def add_log(action, details, level='info'):
    logs = get_logs()
    log_entry = {
        'id': len(logs) + 1,
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'action': action,
        'details': details,
        'level': level,
        'admin': session.get('admin_username', 'system')
    }
    logs.append(log_entry)
    save_logs(logs)

def get_admin_stats():
    users = get_users()
    jobs = get_jobs()
    applications = get_applications()

    # Count total resumes
    total_resumes = 0
    for user_data in users.values():
        total_resumes += len(user_data.get('resumes', []))

    return {
        'total_users': len(users),
        'total_resumes': total_resumes,
        'total_jobs': len(jobs),
        'total_applications': len(applications)
    }

def get_jobs():
    with open('data/jobs.json', 'r') as f:
        return json.load(f)

def get_job_by_id(job_id):
    jobs = get_jobs()
    for job in jobs:
        if job['id'] == job_id:
            return job
    return None

def get_job_categories():
    jobs = get_jobs()
    categories = {}

    for job in jobs:
        category = job.get('category', 'Other')
        if category not in categories:
            categories[category] = []
        categories[category].append(job)

    return categories

# Routes
@app.route('/')
def index():
    return render_template('index.html', logged_in='username' in session)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if user_exists(username):
            flash('Username already exists. Please choose another one.')
            return redirect(url_for('register'))

        users = get_users()
        users[username] = {
            'password': generate_password_hash(password),
            'resumes': []
        }
        save_users(users)

        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = get_users()
        if username in users and check_password_hash(users[username]['password'], password):
            session['username'] = username
            flash('Login successful!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Please log in to access your dashboard.')
        return redirect(url_for('login'))

    users = get_users()
    user_data = users[session['username']]

    return render_template('dashboard.html', user=user_data, username=session['username'])

@app.route('/upload_resume', methods=['GET', 'POST'])
@login_required
def upload_resume():
    if request.method == 'POST':
        try:
            if 'resume' not in request.files:
                flash('No file selected', 'error')
                return redirect(request.url)

            file = request.files['resume']
            if file.filename == '':
                flash('No file selected', 'error')
                return redirect(request.url)

            if not allowed_file(file.filename):
                flash('Invalid file type. Please upload PDF, DOC, DOCX, or TXT files only.', 'error')
                return redirect(request.url)

            filename = secure_filename(file.filename)
            username = session.get('username')
            user_dir = os.path.join('resumes', username)

            try:
                os.makedirs(user_dir, exist_ok=True)
            except Exception as e:
                logger.error(f"Error creating user directory: {str(e)}")
                flash('Error creating directory for resume', 'error')
                return redirect(request.url)

            file_path = os.path.join(user_dir, filename)
            try:
                file.save(file_path)

                # Save resume metadata to user data
                users = get_users()
                if username in users:
                    resume_data = {
                        'name': filename,
                        'filename': filename,
                        'path': file_path,
                        'uploaded_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'file_size': os.path.getsize(file_path),
                        'file_type': filename.split('.')[-1].lower() if '.' in filename else 'unknown'
                    }
                    users[username]['resumes'].append(resume_data)
                    save_users(users)

                flash('Resume uploaded successfully!', 'success')
            except Exception as e:
                logger.error(f"Error saving file: {str(e)}")
                flash('Error saving resume', 'error')
                return redirect(request.url)

            return redirect(url_for('dashboard'))

        except Exception as e:
            logger.error(f"Unexpected error in upload_resume: {str(e)}")
            flash('An unexpected error occurred', 'error')
            return redirect(request.url)

    return render_template('upload_resume.html')

@app.route('/analyze_resume/<int:resume_index>')
def analyze_resume(resume_index):
    if 'username' not in session:
        flash('Please log in to analyze your resume.')
        return redirect(url_for('login'))

    users = get_users()
    user_data = users[session['username']]

    if resume_index >= len(user_data['resumes']):
        flash('Resume not found.')
        return redirect(url_for('dashboard'))

    resume = user_data['resumes'][resume_index]
    file_path = resume['path']

    if not os.path.isfile(file_path):
        flash('Resume file not found.')
        return redirect(url_for('dashboard'))

    # Enhanced document processing
    if ENHANCED_PROCESSING_AVAILABLE:
        # Extract text using enhanced document processor
        resume_text, extraction_success = document_processor.extract_text(file_path)

        if not extraction_success:
            flash('Error extracting text from resume. Please try uploading a different format.', 'error')
            return redirect(url_for('dashboard'))

        # Extract skills using enhanced skill extractor
        resume_skills = skill_extractor.extract_skills(resume_text)

        # Analyze against job descriptions
        job_matches = []
        job_desc_dir = "job_descriptions"

        for filename in os.listdir(job_desc_dir):
            if filename.endswith('.txt'):
                job_id = os.path.splitext(filename)[0]
                job = get_job_by_id(job_id)

                if not job:
                    continue

                job_desc_path = os.path.join(job_desc_dir, filename)

                # Extract job description text
                job_text, job_extraction_success = document_processor.extract_text(job_desc_path)

                if job_extraction_success:
                    # Extract job skills
                    job_skills = skill_extractor.extract_skills(job_text)

                    # Calculate skill match
                    skill_match_results = skill_extractor.calculate_skill_match(resume_skills, job_skills)

                    # Calculate TF-IDF similarity for overall text match
                    text_similarity = calculate_enhanced_similarity(resume_text, job_text)

                    job_matches.append({
                        'job': job,
                        'job_title': job['title'],
                        'company': job['company'],
                        'overall_match': skill_match_results['overall']['percentage'],
                        'text_similarity': text_similarity * 100,
                        'skill_matches': skill_match_results,
                        'missing_skills': skill_extractor.get_skill_suggestions(resume_skills, job_skills)
                    })

        # Sort by overall match percentage
        job_matches.sort(key=lambda x: x['overall_match'], reverse=True)

        # Get top matches
        top_matches = job_matches[:5]

        return render_template('enhanced_results.html',
                             resume_name=resume['name'],
                             resume_skills=resume_skills,
                             job_matches=job_matches,
                             top_matches=top_matches,
                             file_info=document_processor.get_file_info(file_path))

    else:
        # Fallback to old analysis method
        return analyze_resume_fallback(resume_index)

@app.route('/jobs')
def jobs():
    job_categories = get_job_categories()
    return render_template('jobs.html', job_categories=job_categories, logged_in='username' in session)

@app.route('/job/<job_id>')
def job_detail(job_id):
    job = get_job_by_id(job_id)

    if not job:
        flash('Job not found')
        return redirect(url_for('jobs'))

    job_desc_path = os.path.join('job_descriptions', f"{job_id}.txt")

    if not os.path.exists(job_desc_path):
        flash('Job description not found')
        return redirect(url_for('jobs'))

    with open(job_desc_path, 'r', encoding='utf-8') as f:
        job_content = f.read()

    # Parse job_content to extract specific sections
    full_requirements_text = ""
    full_responsibilities_text = ""
    current_section = None

    lines = job_content.splitlines()
    for line in lines:
        if line.strip() == "### Requirements":
            current_section = "requirements"
            continue
        elif line.strip() == "### Responsibilities":
            current_section = "responsibilities"
            continue
        elif line.startswith("###") or line.startswith("##") or line.startswith("#"):
            # Stop capturing if a new major section is encountered
            current_section = None

        if current_section == "requirements":
            full_requirements_text += line + "\n"
        elif current_section == "responsibilities":
            full_responsibilities_text += line + "\n"

    # Basic formatting for lists (lines starting with -)
    def format_list_items(text):
        formatted_lines = []
        for line in text.splitlines():
            if line.strip().startswith('-'):
                formatted_lines.append(f"<li>{line.strip()[1:].strip()}</li>")
            elif line.strip():
                 formatted_lines.append(f"<p>{line.strip()}</p>") # Treat other non-empty lines as paragraphs
        return "<ul>" + "".join(formatted_lines) + "</ul>" if formatted_lines else ""

    # Apply formatting
    formatted_requirements = format_list_items(full_requirements_text)
    formatted_responsibilities = format_list_items(full_responsibilities_text)

    # Pass raw text for debugging
    raw_requirements_text = full_requirements_text
    raw_responsibilities_text = full_responsibilities_text

    # Calculate match score if user is logged in and has uploaded resumes
    if 'username' in session:
        users = get_users()
        user_data = users[session['username']]

        if user_data['resumes']:
            # Use the most recently uploaded resume
            latest_resume = user_data['resumes'][-1]
            resume_path = latest_resume['path']

            if os.path.exists(resume_path):
                match_score = calculate_tfidf_similarity(resume_path, job_desc_path)
                job['match_score'] = match_score

    return render_template('job_detail.html',
                          job=job,
                          job_content=job_content,
                          full_requirements_text=formatted_requirements,
                          full_responsibilities_text=formatted_responsibilities,
                          raw_requirements_text=raw_requirements_text,
                          raw_responsibilities_text=raw_responsibilities_text,
                          logged_in='username' in session)

@app.route('/delete_resume/<resume_name>', methods=['DELETE'])
@login_required
def delete_resume(resume_name):
    try:
        username = session.get('username')
        if not username:
            return jsonify({'error': 'User not logged in'}), 401

        resume_path = os.path.join('resumes', username, secure_filename(resume_name))

        if not os.path.exists(resume_path):
            return jsonify({'error': 'Resume not found'}), 404

        try:
            os.remove(resume_path)
            return jsonify({'message': 'Resume deleted successfully'}), 200
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return jsonify({'error': 'Error deleting resume'}), 500

    except Exception as e:
        logger.error(f"Unexpected error in delete_resume: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

# Add this function for skills extraction
def extract_skills(text):
    # Common technical skills
    technical_skills = {
        'Programming Languages': ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin', 'go', 'rust'],
        'Web Technologies': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring', 'express'],
        'Databases': ['mysql', 'postgresql', 'mongodb', 'sqlite', 'oracle', 'sql server', 'redis'],
        'Cloud Platforms': ['aws', 'azure', 'google cloud', 'heroku', 'digitalocean'],
        'DevOps': ['docker', 'kubernetes', 'jenkins', 'git', 'ci/cd', 'ansible', 'terraform'],
        'Data Science': ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn'],
        'Mobile Development': ['android', 'ios', 'react native', 'flutter', 'xamarin'],
        'Other Skills': ['agile', 'scrum', 'project management', 'ui/ux', 'testing', 'security']
    }

    # Convert text to lowercase for matching
    text = text.lower()

    # Initialize skills dictionary
    found_skills = {category: [] for category in technical_skills.keys()}

    # Find skills in text
    for category, skills in technical_skills.items():
        for skill in skills:
            if skill in text:
                found_skills[category].append(skill)

    return found_skills

@app.route('/analyze_skills/<int:resume_index>')
def analyze_skills(resume_index):
    if 'username' not in session:
        flash('Please log in to analyze your resume.')
        return redirect(url_for('login'))

    users = get_users()
    user_data = users[session['username']]

    if resume_index >= len(user_data['resumes']):
        flash('Resume not found.')
        return redirect(url_for('dashboard'))

    resume = user_data['resumes'][resume_index]
    file_path = resume['path']

    if not os.path.isfile(file_path):
        flash('Resume file not found.')
        return redirect(url_for('dashboard'))

    try:
        # Read resume content
        with open(file_path, 'r', encoding='utf-8') as f:
            resume_content = f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                resume_content = f.read()
        except Exception as e:
            flash('Error reading resume file.')
            return redirect(url_for('dashboard'))

    # Extract skills
    skills = extract_skills(resume_content)

    # Get job requirements for comparison
    job_desc_dir = "job_descriptions"
    job_skills = {}

    for filename in os.listdir(job_desc_dir):
        if filename.endswith('.txt'):
            job_id = os.path.splitext(filename)[0]
            job_path = os.path.join(job_desc_dir, filename)

            try:
                with open(job_path, 'r', encoding='utf-8') as f:
                    job_content = f.read()
                job_skills[job_id] = extract_skills(job_content)
            except Exception as e:
                continue

    # Calculate skill matches
    skill_matches = {}
    for job_id, job_skill_set in job_skills.items():
        match_count = 0
        total_skills = 0

        for category in skills.keys():
            resume_skills = set(skills[category])
            job_skills = set(job_skill_set[category])

            if job_skills:  # Only count if job requires skills in this category
                match_count += len(resume_skills.intersection(job_skills))
                total_skills += len(job_skills)

        if total_skills > 0:
            match_percentage = (match_count / total_skills) * 100
            skill_matches[job_id] = match_percentage

    # Sort jobs by match percentage
    sorted_matches = sorted(skill_matches.items(), key=lambda x: x[1], reverse=True)

    return render_template('skills_analysis.html',
                         skills=skills,
                         skill_matches=sorted_matches,
                         resume_name=resume['name'])

# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admins = get_admins()
        if username in admins and check_password_hash(admins[username]['password'], password):
            if admins[username].get('is_active', True):
                session['admin_username'] = username
                # Update last login
                admins[username]['last_login'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_admins(admins)
                add_log('Admin Login', f'Admin {username} logged in successfully')
                flash('Admin login successful!')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Admin account is deactivated')
        else:
            flash('Invalid admin credentials')
            add_log('Failed Admin Login', f'Failed login attempt for admin: {username}', 'warning')

    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    admin_username = session.get('admin_username')
    if admin_username:
        add_log('Admin Logout', f'Admin {admin_username} logged out')
    session.pop('admin_username', None)
    flash('Admin logged out successfully.')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_login_required
def admin_dashboard():
    stats = get_admin_stats()
    users = get_users()
    jobs = get_jobs()

    # Recent users (last 5)
    recent_users = []
    for username, user_data in list(users.items())[-5:]:
        recent_users.append({
            'username': username,
            'registration_date': user_data.get('created_at', 'N/A'),
            'resume_count': len(user_data.get('resumes', []))
        })

    # Job categories count
    job_categories = {}
    for job in jobs:
        category = job.get('category', 'Other')
        job_categories[category] = job_categories.get(category, 0) + 1

    # Recent activities
    recent_activities = [
        {'icon': 'fas fa-user-plus', 'action': 'New user registered', 'time': '2 hours ago'},
        {'icon': 'fas fa-file-upload', 'action': 'Resume uploaded', 'time': '3 hours ago'},
        {'icon': 'fas fa-briefcase', 'action': 'New job posted', 'time': '5 hours ago'},
        {'icon': 'fas fa-chart-line', 'action': 'Resume analyzed', 'time': '1 day ago'},
    ]

    # System alerts
    system_alerts = [
        {'type': 'info', 'title': 'System Status', 'message': 'All systems operational'},
        {'type': 'warning', 'title': 'Storage Usage', 'message': 'Resume storage at 75% capacity'},
    ]

    return render_template('admin_dashboard.html',
                         stats=stats,
                         recent_users=recent_users,
                         job_categories=job_categories,
                         recent_activities=recent_activities,
                         system_alerts=system_alerts)

@app.route('/admin/users')
@admin_login_required
def admin_users():
    users = get_users()
    user_list = []

    for username, user_data in users.items():
        user_list.append({
            'username': username,
            'email': user_data.get('email', ''),
            'registration_date': user_data.get('created_at', 'N/A'),
            'days_since_registration': 'N/A',
            'resume_count': len(user_data.get('resumes', [])),
            'last_activity': user_data.get('last_login', 'Never'),
            'status': user_data.get('status', 'active')
        })

    # Calculate statistics
    stats = {
        'total_users': len(users),
        'active_users': len([u for u in user_list if u['status'] == 'active']),
        'users_with_resumes': len([u for u in user_list if u['resume_count'] > 0]),
        'recent_registrations': len([u for u in user_list if u['registration_date'] != 'N/A'])  # Simplified
    }

    return render_template('admin_users.html', users=user_list, stats=stats)

@app.route('/admin/users/<username>')
@admin_login_required
def admin_user_detail(username):
    users = get_users()
    if username not in users:
        flash('User not found')
        return redirect(url_for('admin_users'))

    user_data = users[username]
    user_info = {
        'username': username,
        'email': user_data.get('email', 'N/A'),
        'registration_date': user_data.get('created_at', 'N/A'),
        'last_login': user_data.get('last_login', 'Never'),
        'status': user_data.get('status', 'active'),
        'resumes': user_data.get('resumes', []),
        'resume_count': len(user_data.get('resumes', []))
    }

    return jsonify(user_info)

@app.route('/admin/users/<username>/toggle-status', methods=['POST'])
@admin_login_required
def admin_toggle_user_status(username):
    try:
        users = get_users()
        if username not in users:
            return jsonify({'success': False, 'error': 'User not found'})

        data = request.get_json()
        new_status = data.get('status')

        if new_status not in ['active', 'inactive']:
            return jsonify({'success': False, 'error': 'Invalid status'})

        users[username]['status'] = new_status
        save_users(users)

        action = 'activated' if new_status == 'active' else 'deactivated'
        add_log('User Status Change', f'User {username} {action} by admin')

        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error toggling user status: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'})

@app.route('/admin/users/<username>/delete', methods=['DELETE'])
@admin_login_required
def admin_delete_user(username):
    try:
        users = get_users()
        if username not in users:
            return jsonify({'success': False, 'error': 'User not found'})

        # Delete user's resume files
        user_resume_dir = os.path.join('resumes', username)
        if os.path.exists(user_resume_dir):
            import shutil
            shutil.rmtree(user_resume_dir)

        # Delete user from database
        del users[username]
        save_users(users)

        add_log('User Deletion', f'User {username} deleted by admin', 'warning')

        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'})



@app.route('/admin/users/export')
@admin_login_required
def admin_export_users():
    try:
        users = get_users()

        # Create CSV content
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(['Username', 'Email', 'Registration Date', 'Last Login', 'Status', 'Resume Count'])

        # Write user data
        for username, user_data in users.items():
            writer.writerow([
                username,
                user_data.get('email', ''),
                user_data.get('created_at', ''),
                user_data.get('last_login', 'Never'),
                user_data.get('status', 'active'),
                len(user_data.get('resumes', []))
            ])

        output.seek(0)

        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=users_export.csv'}
        )
    except Exception as e:
        logger.error(f"Error exporting users: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'})

@app.route('/admin/users/add', methods=['POST'])
@admin_login_required
def admin_add_user():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email', '')
        password = data.get('password')
        status = data.get('status', 'active')

        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password are required'})

        users = get_users()
        if username in users:
            return jsonify({'success': False, 'error': 'Username already exists'})

        # Create new user
        users[username] = {
            'password': generate_password_hash(password),
            'email': email,
            'created_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': status,
            'resumes': []
        }

        save_users(users)
        add_log('User Creation', f'User {username} created by admin')

        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error adding user: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'})

@app.route('/admin/users/bulk-delete', methods=['DELETE'])
@admin_login_required
def admin_bulk_delete_users():
    try:
        data = request.get_json()
        usernames = data.get('usernames', [])

        if not usernames:
            return jsonify({'success': False, 'error': 'No users selected'})

        users = get_users()
        deleted_count = 0

        for username in usernames:
            if username in users:
                # Delete user's resume files
                user_resume_dir = os.path.join('resumes', username)
                if os.path.exists(user_resume_dir):
                    import shutil
                    shutil.rmtree(user_resume_dir)

                # Delete user from database
                del users[username]
                deleted_count += 1

        save_users(users)
        add_log('Bulk User Deletion', f'{deleted_count} users deleted by admin', 'warning')

        return jsonify({'success': True, 'deleted_count': deleted_count})
    except Exception as e:
        logger.error(f"Error bulk deleting users: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'})

@app.route('/admin/users/<username>/reset-password', methods=['POST'])
@admin_login_required
def admin_reset_user_password(username):
    try:
        users = get_users()
        if username not in users:
            return jsonify({'success': False, 'error': 'User not found'})

        # Generate a temporary password
        import secrets
        import string
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

        # Update user password
        users[username]['password'] = generate_password_hash(temp_password)
        save_users(users)

        add_log('Password Reset', f'Password reset for user {username} by admin')

        return jsonify({'success': True, 'temporary_password': temp_password})
    except Exception as e:
        logger.error(f"Error resetting password: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'})

@app.route('/admin/resumes')
@admin_login_required
def admin_resumes():
    users = get_users()
    resume_list = []
    total_size = 0

    for username, user_data in users.items():
        for resume in user_data.get('resumes', []):
            # Get file info
            file_path = resume.get('path', '')
            file_size = 0
            file_type = 'unknown'

            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                file_type = file_path.split('.')[-1].lower() if '.' in file_path else 'unknown'

            total_size += file_size

            resume_list.append({
                'id': f"{username}_{resume.get('filename', '')}",
                'name': resume.get('name', 'Unnamed'),
                'filename': resume.get('filename', ''),
                'username': username,
                'upload_date': resume.get('uploaded_at', 'N/A'),
                'days_ago': 'N/A',
                'file_size': f"{file_size / 1024:.1f} KB" if file_size > 0 else 'N/A',
                'file_type': file_type,
                'analysis_status': 'completed'  # Simplified for now
            })

    # Calculate statistics
    stats = {
        'total_resumes': len(resume_list),
        'analyzed_resumes': len([r for r in resume_list if r['analysis_status'] == 'completed']),
        'pending_analysis': len([r for r in resume_list if r['analysis_status'] == 'pending']),
        'total_size_mb': f"{total_size / (1024 * 1024):.1f}"
    }

    return render_template('admin_resumes.html', resumes=resume_list, stats=stats)

@app.route('/admin/resumes/<username>/<filename>/delete', methods=['DELETE'])
@admin_login_required
def admin_delete_resume(username, filename):
    try:
        users = get_users()
        if username not in users:
            return jsonify({'success': False, 'error': 'User not found'})

        user_data = users[username]
        resumes = user_data.get('resumes', [])

        # Find and remove the resume
        resume_to_remove = None
        for i, resume in enumerate(resumes):
            if resume.get('filename') == filename:
                resume_to_remove = i
                break

        if resume_to_remove is None:
            return jsonify({'success': False, 'error': 'Resume not found'})

        # Delete the file
        resume_path = resumes[resume_to_remove].get('path', '')
        if os.path.exists(resume_path):
            os.remove(resume_path)

        # Remove from database
        del resumes[resume_to_remove]
        users[username]['resumes'] = resumes
        save_users(users)

        add_log('Resume Deletion', f'Resume {filename} deleted from user {username} by admin', 'warning')

        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error deleting resume: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'})

@app.route('/admin/jobs')
@admin_login_required
def admin_jobs():
    jobs = get_jobs()

    # Add status field if not present
    for job in jobs:
        if 'status' not in job:
            job['status'] = 'active'

    # Get categories
    categories = list(set(job.get('category', 'Other') for job in jobs))

    # Calculate statistics
    stats = {
        'total_jobs': len(jobs),
        'active_jobs': len([j for j in jobs if j.get('status', 'active') == 'active']),
        'categories': len(categories),
        'recent_posts': len([j for j in jobs if j.get('date_posted', '') == datetime.datetime.now().strftime("%Y-%m-%d")])
    }

    return render_template('admin_jobs.html', jobs=jobs, categories=categories, stats=stats)

@app.route('/admin/jobs/<job_id>')
@admin_login_required
def admin_job_detail(job_id):
    job = get_job_by_id(job_id)
    if not job:
        return jsonify({'success': False, 'error': 'Job not found'})

    return jsonify({'success': True, 'job': job})

@app.route('/admin/jobs/add', methods=['POST'])
@admin_login_required
def admin_add_job():
    try:
        data = request.get_json()
        jobs = get_jobs()

        # Generate job ID
        job_id = f"{data['company'].lower().replace(' ', '-')}-{data['title'].lower().replace(' ', '-')}"

        new_job = {
            'id': job_id,
            'company': data['company'],
            'title': data['title'],
            'category': data['category'],
            'location': data['location'],
            'experience': data['experience'],
            'salary': data['salary'],
            'description': data['description'],
            'date_posted': datetime.datetime.now().strftime("%Y-%m-%d"),
            'status': 'active'
        }

        jobs.append(new_job)

        # Save to jobs.json
        with open('data/jobs.json', 'w') as f:
            json.dump(jobs, f, indent=4)

        # Create job description file
        job_desc_path = os.path.join('job_descriptions', f"{job_id}.txt")
        with open(job_desc_path, 'w', encoding='utf-8') as f:
            f.write(f"# {new_job['company']}\n\n")
            f.write(f"## {new_job['title']}\n\n")
            f.write(f"**Location:** {new_job['location']}\n")
            f.write(f"**Experience Required:** {new_job['experience']}\n")
            f.write(f"**Salary:** {new_job['salary']}\n\n")
            f.write(f"### Company Overview\n\n{new_job['description']}\n\n")
            f.write("### Job Description\n\nWe are looking for a talented and motivated professional to join our team.\n\n")
            f.write("### Requirements\n\n- Relevant experience in the field\n- Strong problem-solving abilities\n- Excellent communication skills\n\n")
            f.write("### Benefits\n\n- Competitive salary package\n- Health insurance\n- Professional development opportunities\n")

        add_log('Job Creation', f'New job "{new_job["title"]}" at {new_job["company"]} created by admin')

        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error adding job: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'})

@app.route('/admin/jobs/<job_id>/update', methods=['PUT'])
@admin_login_required
def admin_update_job(job_id):
    try:
        data = request.get_json()
        jobs = get_jobs()

        # Find the job to update
        job_index = None
        for i, job in enumerate(jobs):
            if job['id'] == job_id:
                job_index = i
                break

        if job_index is None:
            return jsonify({'success': False, 'error': 'Job not found'})

        # Update job data
        jobs[job_index].update({
            'company': data['company'],
            'title': data['title'],
            'category': data['category'],
            'location': data['location'],
            'experience': data['experience'],
            'salary': data['salary'],
            'description': data['description']
        })

        # Save to jobs.json
        with open('data/jobs.json', 'w') as f:
            json.dump(jobs, f, indent=4)

        # Update job description file
        job_desc_path = os.path.join('job_descriptions', f"{job_id}.txt")
        with open(job_desc_path, 'w', encoding='utf-8') as f:
            f.write(f"# {jobs[job_index]['company']}\n\n")
            f.write(f"## {jobs[job_index]['title']}\n\n")
            f.write(f"**Location:** {jobs[job_index]['location']}\n")
            f.write(f"**Experience Required:** {jobs[job_index]['experience']}\n")
            f.write(f"**Salary:** {jobs[job_index]['salary']}\n\n")
            f.write(f"### Company Overview\n\n{jobs[job_index]['description']}\n\n")
            f.write("### Job Description\n\nWe are looking for a talented and motivated professional to join our team.\n\n")
            f.write("### Requirements\n\n- Relevant experience in the field\n- Strong problem-solving abilities\n- Excellent communication skills\n\n")
            f.write("### Benefits\n\n- Competitive salary package\n- Health insurance\n- Professional development opportunities\n")

        add_log('Job Update', f'Job "{jobs[job_index]["title"]}" at {jobs[job_index]["company"]} updated by admin')

        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error updating job: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'})

@app.route('/admin/jobs/<job_id>/delete', methods=['DELETE'])
@admin_login_required
def admin_delete_job(job_id):
    try:
        jobs = get_jobs()

        # Find the job to delete
        job_to_delete = None
        for i, job in enumerate(jobs):
            if job['id'] == job_id:
                job_to_delete = jobs.pop(i)
                break

        if job_to_delete is None:
            return jsonify({'success': False, 'error': 'Job not found'})

        # Save updated jobs list
        with open('data/jobs.json', 'w') as f:
            json.dump(jobs, f, indent=4)

        # Delete job description file
        job_desc_path = os.path.join('job_descriptions', f"{job_id}.txt")
        if os.path.exists(job_desc_path):
            os.remove(job_desc_path)

        add_log('Job Deletion', f'Job "{job_to_delete["title"]}" at {job_to_delete["company"]} deleted by admin')

        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error deleting job: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'})

@app.route('/admin/jobs/<job_id>/toggle-status', methods=['POST'])
@admin_login_required
def admin_toggle_job_status(job_id):
    try:
        data = request.get_json()
        new_status = data.get('status')
        jobs = get_jobs()

        if new_status not in ['active', 'expired']:
            return jsonify({'success': False, 'error': 'Invalid status'})

        # Find the job to update
        job_index = None
        for i, job in enumerate(jobs):
            if job['id'] == job_id:
                job_index = i
                break

        if job_index is None:
            return jsonify({'success': False, 'error': 'Job not found'})

        # Update job status
        jobs[job_index]['status'] = new_status

        # Save to jobs.json
        with open('data/jobs.json', 'w') as f:
            json.dump(jobs, f, indent=4)

        add_log('Job Status Update', f'Job "{jobs[job_index]["title"]}" status changed to {new_status} by admin')

        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error toggling job status: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'})

@app.route('/admin/jobs/bulk-delete', methods=['DELETE'])
@admin_login_required
def admin_bulk_delete_jobs():
    try:
        data = request.get_json()
        job_ids = data.get('job_ids', [])

        if not job_ids:
            return jsonify({'success': False, 'error': 'No jobs selected'})

        jobs = get_jobs()
        deleted_jobs = []

        # Remove jobs and collect deleted job info
        jobs_to_keep = []
        for job in jobs:
            if job['id'] in job_ids:
                deleted_jobs.append(job)
                # Delete job description file
                job_desc_path = os.path.join('job_descriptions', f"{job['id']}.txt")
                if os.path.exists(job_desc_path):
                    os.remove(job_desc_path)
            else:
                jobs_to_keep.append(job)

        # Save updated jobs list
        with open('data/jobs.json', 'w') as f:
            json.dump(jobs_to_keep, f, indent=4)

        add_log('Bulk Job Deletion', f'{len(deleted_jobs)} jobs deleted by admin')

        return jsonify({'success': True, 'deleted_count': len(deleted_jobs)})
    except Exception as e:
        logger.error(f"Error bulk deleting jobs: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'})

@app.route('/admin/jobs/export')
@admin_login_required
def admin_export_jobs():
    try:
        jobs = get_jobs()

        # Create CSV content
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(['ID', 'Title', 'Company', 'Category', 'Location', 'Experience', 'Salary', 'Status', 'Date Posted'])

        # Write job data
        for job in jobs:
            writer.writerow([
                job.get('id', ''),
                job.get('title', ''),
                job.get('company', ''),
                job.get('category', ''),
                job.get('location', ''),
                job.get('experience', ''),
                job.get('salary', ''),
                job.get('status', 'active'),
                job.get('date_posted', '')
            ])

        output.seek(0)

        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=jobs_export.csv'}
        )
    except Exception as e:
        logger.error(f"Error exporting jobs: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'})



@app.route('/admin/settings')
@admin_login_required
def admin_settings():
    import sys
    import flask

    # Get system information
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    flask_version = flask.__version__
    uptime = "N/A"  # Simplified for now

    # Get storage information
    stats = get_admin_stats()
    storage_info = {
        'total_users': stats['total_users'],
        'total_resumes': stats['total_resumes'],
        'total_jobs': stats['total_jobs'],
        'storage_used': 'N/A'  # Simplified for now
    }

    return render_template('admin_settings.html',
                         python_version=python_version,
                         flask_version=flask_version,
                         uptime=uptime,
                         storage_info=storage_info)

@app.route('/admin/settings/change-password', methods=['POST'])
@admin_login_required
def admin_change_password():
    try:
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')

        admin_username = session.get('admin_username')
        admins = get_admins()

        if admin_username not in admins:
            return jsonify({'success': False, 'error': 'Admin not found'})

        # Verify current password
        if not check_password_hash(admins[admin_username]['password'], current_password):
            return jsonify({'success': False, 'error': 'Current password is incorrect'})

        # Update password
        admins[admin_username]['password'] = generate_password_hash(new_password)
        save_admins(admins)

        add_log('Password Change', f'Admin {admin_username} changed password')

        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'})

@app.route('/admin/logs')
@admin_login_required
def admin_logs():
    logs = get_logs()
    # Sort logs by timestamp (most recent first)
    logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return render_template('admin_logs.html', logs=logs)

@app.route('/admin/logs/clear', methods=['POST'])
@admin_login_required
def admin_clear_logs():
    try:
        save_logs([])  # Clear all logs
        add_log('Logs Cleared', 'All system logs cleared by admin')
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error clearing logs: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'})

@app.route('/admin/applications')
@admin_login_required
def admin_applications():
    applications = get_applications()
    jobs = get_jobs()

    # Calculate statistics
    stats = {
        'total_applications': len(applications),
        'pending_applications': len([a for a in applications if a.get('status') == 'pending']),
        'reviewed_applications': len([a for a in applications if a.get('status') == 'reviewed']),
        'rejected_applications': len([a for a in applications if a.get('status') == 'rejected'])
    }

    return render_template('admin_applications.html',
                         applications=applications,
                         jobs=jobs,
                         stats=stats)

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)

    app.run(host='localhost', port=5000, debug=True)