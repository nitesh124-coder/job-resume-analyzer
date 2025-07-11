"""
Enhanced Skill Extraction Module for Resume Analysis
Provides comprehensive skill detection and categorization
"""

import re
import logging
from typing import Dict, List, Set, Tuple
from collections import defaultdict

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SkillExtractor:
    """
    Advanced skill extraction with comprehensive skill databases and pattern matching
    """
    
    def __init__(self):
        self.skill_database = self._build_skill_database()
        self.skill_patterns = self._build_skill_patterns()
    
    def _build_skill_database(self) -> Dict[str, List[str]]:
        """Build comprehensive skill database with categories"""
        return {
            'Programming Languages': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c', 'ruby', 'php', 
                'swift', 'kotlin', 'go', 'rust', 'scala', 'perl', 'r', 'matlab', 'vba',
                'objective-c', 'dart', 'lua', 'haskell', 'clojure', 'f#', 'cobol', 'fortran',
                'assembly', 'shell', 'bash', 'powershell', 'sql', 'plsql', 'tsql'
            ],
            'Web Technologies': [
                'html', 'html5', 'css', 'css3', 'sass', 'scss', 'less', 'bootstrap', 'tailwind',
                'react', 'reactjs', 'angular', 'angularjs', 'vue', 'vuejs', 'svelte', 'ember',
                'node.js', 'nodejs', 'express', 'expressjs', 'django', 'flask', 'fastapi',
                'spring', 'spring boot', 'laravel', 'symfony', 'codeigniter', 'rails',
                'asp.net', 'mvc', 'web api', 'rest api', 'graphql', 'soap', 'ajax', 'json',
                'xml', 'jquery', 'webpack', 'gulp', 'grunt', 'npm', 'yarn', 'bower'
            ],
            'Databases': [
                'mysql', 'postgresql', 'sqlite', 'oracle', 'sql server', 'mongodb', 'redis',
                'cassandra', 'dynamodb', 'elasticsearch', 'neo4j', 'couchdb', 'firebase',
                'mariadb', 'db2', 'sybase', 'access', 'snowflake', 'bigquery', 'redshift'
            ],
            'Cloud Platforms': [
                'aws', 'amazon web services', 'azure', 'microsoft azure', 'google cloud',
                'gcp', 'heroku', 'digitalocean', 'linode', 'vultr', 'cloudflare',
                'ec2', 's3', 'lambda', 'rds', 'cloudformation', 'terraform', 'ansible'
            ],
            'DevOps & Tools': [
                'docker', 'kubernetes', 'k8s', 'jenkins', 'git', 'github', 'gitlab', 'bitbucket',
                'ci/cd', 'continuous integration', 'continuous deployment', 'ansible', 'terraform',
                'vagrant', 'chef', 'puppet', 'nagios', 'prometheus', 'grafana', 'elk stack',
                'linux', 'unix', 'ubuntu', 'centos', 'redhat', 'debian', 'windows server',
                'apache', 'nginx', 'tomcat', 'iis', 'load balancing', 'microservices'
            ],
            'Data Science & Analytics': [
                'machine learning', 'deep learning', 'artificial intelligence', 'ai', 'ml',
                'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy', 'scipy',
                'matplotlib', 'seaborn', 'plotly', 'tableau', 'power bi', 'qlik', 'looker',
                'jupyter', 'anaconda', 'spark', 'hadoop', 'kafka', 'airflow', 'dbt',
                'statistics', 'data mining', 'data visualization', 'etl', 'data warehouse',
                'big data', 'nlp', 'computer vision', 'neural networks', 'regression',
                'classification', 'clustering', 'time series', 'forecasting'
            ],
            'Mobile Development': [
                'android', 'ios', 'react native', 'flutter', 'xamarin', 'ionic', 'cordova',
                'phonegap', 'swift', 'objective-c', 'kotlin', 'java', 'dart', 'mobile app',
                'app store', 'google play', 'mobile ui', 'responsive design'
            ],
            'Testing & Quality': [
                'unit testing', 'integration testing', 'automation testing', 'selenium',
                'cypress', 'jest', 'mocha', 'jasmine', 'pytest', 'junit', 'testng',
                'cucumber', 'postman', 'api testing', 'load testing', 'performance testing',
                'security testing', 'penetration testing', 'qa', 'quality assurance',
                'tdd', 'bdd', 'test driven development', 'behavior driven development'
            ],
            'Project Management': [
                'agile', 'scrum', 'kanban', 'waterfall', 'project management', 'pmp',
                'jira', 'confluence', 'trello', 'asana', 'monday.com', 'slack', 'teams',
                'stakeholder management', 'risk management', 'budget management',
                'resource planning', 'sprint planning', 'retrospectives', 'stand-ups'
            ],
            'Design & UX': [
                'ui/ux', 'user interface', 'user experience', 'wireframing', 'prototyping',
                'figma', 'sketch', 'adobe xd', 'invision', 'photoshop', 'illustrator',
                'after effects', 'premiere pro', 'canva', 'user research', 'usability testing',
                'information architecture', 'interaction design', 'visual design',
                'responsive design', 'accessibility', 'material design', 'human-centered design'
            ],
            'Security': [
                'cybersecurity', 'information security', 'network security', 'application security',
                'penetration testing', 'vulnerability assessment', 'ethical hacking', 'cissp',
                'ceh', 'security+', 'firewall', 'intrusion detection', 'encryption', 'ssl/tls',
                'oauth', 'jwt', 'authentication', 'authorization', 'compliance', 'gdpr',
                'hipaa', 'sox', 'iso 27001', 'nist', 'owasp'
            ],
            'Business & Soft Skills': [
                'leadership', 'team management', 'communication', 'problem solving',
                'analytical thinking', 'critical thinking', 'decision making', 'negotiation',
                'presentation', 'public speaking', 'mentoring', 'coaching', 'training',
                'customer service', 'sales', 'marketing', 'business analysis', 'requirements gathering',
                'process improvement', 'change management', 'strategic planning', 'budgeting',
                'financial analysis', 'vendor management', 'contract negotiation'
            ]
        }
    
    def _build_skill_patterns(self) -> Dict[str, re.Pattern]:
        """Build regex patterns for better skill detection"""
        patterns = {}
        
        # Programming language patterns
        patterns['programming'] = re.compile(
            r'\b(?:programming|coding|development|scripting)\s+(?:in\s+|with\s+|using\s+)?'
            r'([a-zA-Z+#\.]+(?:\s+[a-zA-Z+#\.]+)*)\b',
            re.IGNORECASE
        )
        
        # Framework patterns
        patterns['framework'] = re.compile(
            r'\b(?:framework|library|platform|tool|technology):\s*([a-zA-Z\.\-\s]+)\b',
            re.IGNORECASE
        )
        
        # Experience patterns
        patterns['experience'] = re.compile(
            r'\b(\d+)\s*(?:\+)?\s*years?\s+(?:of\s+)?(?:experience\s+)?(?:in\s+|with\s+|using\s+)?'
            r'([a-zA-Z+#\.\-\s]+)\b',
            re.IGNORECASE
        )
        
        # Certification patterns
        patterns['certification'] = re.compile(
            r'\b(?:certified|certification|certificate)\s+(?:in\s+)?([a-zA-Z\s\-\+]+)\b',
            re.IGNORECASE
        )
        
        return patterns
    
    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """
        Extract skills from text using multiple methods
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            Dict[str, List[str]]: Categorized skills found in text
        """
        if not text:
            return {category: [] for category in self.skill_database.keys()}
        
        text_lower = text.lower()
        found_skills = defaultdict(set)
        
        # Method 1: Direct keyword matching
        self._extract_direct_keywords(text_lower, found_skills)
        
        # Method 2: Pattern-based extraction
        self._extract_pattern_based(text, found_skills)
        
        # Method 3: Context-aware extraction
        self._extract_context_aware(text_lower, found_skills)
        
        # Convert sets to sorted lists and return
        result = {}
        for category in self.skill_database.keys():
            result[category] = sorted(list(found_skills[category]))
        
        return result
    
    def _extract_direct_keywords(self, text: str, found_skills: defaultdict):
        """Extract skills using direct keyword matching"""
        for category, skills in self.skill_database.items():
            for skill in skills:
                # Use word boundaries for exact matches
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text):
                    found_skills[category].add(skill)
    
    def _extract_pattern_based(self, text: str, found_skills: defaultdict):
        """Extract skills using regex patterns"""
        for pattern_name, pattern in self.skill_patterns.items():
            matches = pattern.findall(text)
            for match in matches:
                if isinstance(match, tuple):
                    skill_text = match[-1]  # Get the last group (the skill)
                else:
                    skill_text = match
                
                # Check if extracted text matches any known skills
                self._match_extracted_text(skill_text.lower().strip(), found_skills)
    
    def _extract_context_aware(self, text: str, found_skills: defaultdict):
        """Extract skills using context-aware methods"""
        # Look for skills in common contexts
        contexts = [
            r'skills?:?\s*([^\.]+)',
            r'technologies?:?\s*([^\.]+)',
            r'tools?:?\s*([^\.]+)',
            r'languages?:?\s*([^\.]+)',
            r'frameworks?:?\s*([^\.]+)',
            r'platforms?:?\s*([^\.]+)',
            r'databases?:?\s*([^\.]+)',
            r'experience\s+(?:in|with):?\s*([^\.]+)',
            r'proficient\s+(?:in|with):?\s*([^\.]+)',
            r'familiar\s+with:?\s*([^\.]+)',
            r'knowledge\s+of:?\s*([^\.]+)'
        ]
        
        for context_pattern in contexts:
            matches = re.finditer(context_pattern, text, re.IGNORECASE)
            for match in matches:
                context_text = match.group(1).lower().strip()
                self._match_extracted_text(context_text, found_skills)
    
    def _match_extracted_text(self, text: str, found_skills: defaultdict):
        """Match extracted text against skill database"""
        # Split by common separators
        potential_skills = re.split(r'[,;|&\n\r]+', text)
        
        for potential_skill in potential_skills:
            potential_skill = potential_skill.strip()
            if len(potential_skill) < 2:  # Skip very short strings
                continue
            
            # Check against all skills in database
            for category, skills in self.skill_database.items():
                for skill in skills:
                    if skill.lower() in potential_skill or potential_skill in skill.lower():
                        found_skills[category].add(skill)
    
    def calculate_skill_match(self, resume_skills: Dict[str, List[str]], 
                            job_skills: Dict[str, List[str]]) -> Dict[str, float]:
        """
        Calculate skill match percentage between resume and job requirements
        
        Args:
            resume_skills: Skills extracted from resume
            job_skills: Skills extracted from job description
            
        Returns:
            Dict with match percentages by category and overall
        """
        match_results = {}
        total_matches = 0
        total_required = 0
        
        for category in self.skill_database.keys():
            resume_set = set(skill.lower() for skill in resume_skills.get(category, []))
            job_set = set(skill.lower() for skill in job_skills.get(category, []))
            
            if job_set:  # Only calculate if job requires skills in this category
                matches = len(resume_set.intersection(job_set))
                required = len(job_set)
                match_percentage = (matches / required) * 100 if required > 0 else 0
                
                match_results[category] = {
                    'percentage': round(match_percentage, 1),
                    'matches': matches,
                    'required': required,
                    'matched_skills': list(resume_set.intersection(job_set))
                }
                
                total_matches += matches
                total_required += required
        
        # Calculate overall match
        overall_percentage = (total_matches / total_required) * 100 if total_required > 0 else 0
        match_results['overall'] = {
            'percentage': round(overall_percentage, 1),
            'total_matches': total_matches,
            'total_required': total_required
        }
        
        return match_results
    
    def get_skill_suggestions(self, current_skills: Dict[str, List[str]], 
                            target_job_skills: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Suggest skills to learn based on job requirements
        
        Args:
            current_skills: Current skills from resume
            target_job_skills: Required skills from job description
            
        Returns:
            Dict of suggested skills by category
        """
        suggestions = {}
        
        for category in self.skill_database.keys():
            current_set = set(skill.lower() for skill in current_skills.get(category, []))
            required_set = set(skill.lower() for skill in target_job_skills.get(category, []))
            
            # Find missing skills
            missing_skills = required_set - current_set
            if missing_skills:
                suggestions[category] = list(missing_skills)
        
        return suggestions

# Global instance for easy import
skill_extractor = SkillExtractor()
