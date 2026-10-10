import sqlite3
import os
import json
import hashlib
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "app.db")

def hash_password(password: str) -> str:
    """Hash password with sha256 and salt."""
    salt = "ai_resume_matcher_salt_2026"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'candidate', -- 'candidate', 'recruiter', 'admin'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Jobs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        department TEXT NOT NULL,
        experience_required TEXT NOT NULL,
        description TEXT NOT NULL,
        required_skills TEXT NOT NULL, -- JSON list of skills
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Evaluations Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        candidate_name TEXT NOT NULL,
        job_id INTEGER,
        job_title TEXT NOT NULL,
        match_score REAL NOT NULL,
        skill_score REAL NOT NULL,
        tfidf_score REAL NOT NULL,
        matched_skills TEXT NOT NULL, -- JSON list
        missing_skills TEXT NOT NULL, -- JSON list
        bonus_skills TEXT NOT NULL,   -- JSON list
        verdict TEXT NOT NULL,
        recommendations TEXT NOT NULL, -- JSON list
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()

    # Seed Default Users if not present
    seed_users = [
        ("admin", "admin@resumematcher.ai", "admin123", "System Administrator", "admin"),
        ("recruiter", "talent@techcorp.com", "recruiter123", "Sarah Jenkins (Talent Lead)", "recruiter"),
        ("candidate", "candidate@gmail.com", "candidate123", "Alex Morgan", "candidate")
    ]
    for username, email, pwd, name, role in seed_users:
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, full_name, role) VALUES (?, ?, ?, ?, ?)",
                (username, email, hash_password(pwd), name, role)
            )

    # Seed Sample Jobs if none exist
    cursor.execute("SELECT COUNT(*) as count FROM jobs")
    if cursor.fetchone()["count"] == 0:
        sample_jobs = [
            (
                "Senior Machine Learning Engineer",
                "DeepLogic AI",
                "Artificial Intelligence / Data Science",
                "4+ years",
                """We are seeking a Senior Machine Learning Engineer to design, deploy, and scale production AI systems and NLP pipelines.
Responsibilities:
- Build and fine-tune transformer models, LLMs, and NLP architectures using PyTorch and HuggingFace.
- Implement feature extraction, TF-IDF vectorization, semantic embeddings, and vector databases.
- Develop scalable REST APIs with FastAPI and Docker for model inference.
- Collaborate with MLOps pipelines using CI/CD, Kubernetes, and AWS cloud services.
Requirements:
- Strong proficiency in Python, NumPy, Pandas, Scikit-Learn, and PyTorch or TensorFlow.
- Experience with Natural Language Processing (NLP), tokenization, text embeddings, and Transformers.
- Familiarity with Docker, Kubernetes, AWS, Git, and RESTful APIs.
- Excellent problem-solving skills and teamwork.""",
                json.dumps(["Python", "Machine Learning", "NLP", "PyTorch", "Scikit-Learn", "FastAPI", "Docker", "AWS", "Transformers", "Git"])
            ),
            (
                "Full Stack Python & React Developer",
                "CloudVenture Technologies",
                "Software Engineering",
                "3+ years",
                """We are looking for a versatile Full Stack Developer to build modern cloud applications.
Responsibilities:
- Build responsive frontend dashboards with React, JavaScript, modern CSS, and HTML5.
- Develop high-performance backend microservices with Python, FastAPI or Django, and PostgreSQL.
- Implement user authentication, role-based access control, and RESTful APIs.
- Deploy applications using Docker, Linux, and automated CI/CD pipelines.
Requirements:
- Hands-on experience with Python, React, JavaScript, HTML, CSS, and TypeScript.
- Strong knowledge of relational databases (PostgreSQL or MySQL) and Redis caching.
- Familiarity with Git, Docker, REST APIs, and Agile development methodology.
- Strong communication and analytical mindset.""",
                json.dumps(["Python", "React", "JavaScript", "FastAPI", "PostgreSQL", "Docker", "HTML", "CSS", "Git", "REST API"])
            ),
            (
                "Cloud DevOps & Platform Engineer",
                "OmniScale Infrastructure",
                "DevOps & Infrastructure",
                "3-5 years",
                """Join our platform team as a Cloud DevOps Engineer to automate and scale our infrastructure.
Responsibilities:
- Architect reliable cloud infrastructure on AWS and Azure using Terraform and Ansible.
- Manage Kubernetes clusters, Helm charts, and containerized microservices.
- Design CI/CD release pipelines with GitHub Actions and Jenkins.
- Monitor system reliability, Linux systems performance, and automated logging.
Requirements:
- Deep expertise in AWS, Docker, Kubernetes, Terraform, Linux, and Bash scripting.
- Experience with CI/CD tools (GitHub Actions, Jenkins) and Python automation.
- Knowledge of cloud networking, security, and Git.""",
                json.dumps(["AWS", "Docker", "Kubernetes", "Terraform", "Linux", "CI/CD", "GitHub Actions", "Python", "Bash"])
            ),
            (
                "Data Analyst & BI Specialist",
                "InsightMetrics Global",
                "Business Intelligence",
                "2+ years",
                """Looking for a Data Analyst to translate complex business data into actionable insights and executive dashboards.
Responsibilities:
- Query large datasets using SQL and optimize analytical reporting queries.
- Perform exploratory data analysis using Python, Pandas, and NumPy.
- Design interactive visualization dashboards using Tableau and PowerBI.
- Present data-driven findings to cross-functional stakeholders.
Requirements:
- Advanced SQL querying, data modeling, and database management.
- Python scripting with Pandas, NumPy, and Matplotlib.
- Expertise in PowerBI or Tableau dashboards.
- Problem solving, critical thinking, and business communication.""",
                json.dumps(["SQL", "Python", "Pandas", "PowerBI", "Tableau", "NumPy", "Data Warehousing", "Excel"])
            )
        ]
        for title, company, dept, exp, desc, skills in sample_jobs:
            cursor.execute(
                "INSERT INTO jobs (title, company, department, experience_required, description, required_skills, created_by) VALUES (?, ?, ?, ?, ?, ?, 1)",
                (title, company, dept, exp, desc, skills)
            )

    # Seed Sample Past Evaluations for realistic admin dashboard statistics
    cursor.execute("SELECT COUNT(*) as count FROM evaluations")
    if cursor.fetchone()["count"] == 0:
        sample_evals = [
            (
                1, "Vikram Sharma", 1, "Senior Machine Learning Engineer", 88.5, 90.0, 86.2,
                json.dumps(["Python", "Machine Learning", "NLP", "PyTorch", "Scikit-Learn", "FastAPI", "Docker", "Git"]),
                json.dumps(["Transformers", "AWS"]),
                json.dumps(["TensorFlow", "Pandas", "NumPy", "Flask"]),
                "Strong Match - High Priority",
                json.dumps([
                    "Include specific metrics for HuggingFace/Transformer models in recent projects.",
                    "Highlight any AWS cloud deployment experience (SageMaker or ECS).",
                    "Add keywords: Transformers, AWS to increase ATS relevance."
                ])
            ),
            (
                1, "Ananya Rao", 2, "Full Stack Python & React Developer", 92.0, 95.0, 87.5,
                json.dumps(["Python", "React", "JavaScript", "FastAPI", "PostgreSQL", "HTML", "CSS", "Git", "REST API"]),
                json.dumps(["Docker"]),
                json.dumps(["Redux", "TailwindCSS", "Node.js", "SQLite"]),
                "Strong Match - High Priority",
                json.dumps([
                    "Candidate satisfies 90% of core technical requirements.",
                    "Consider mentioning Docker containerization workflows."
                ])
            ),
            (
                1, "David Miller", 1, "Senior Machine Learning Engineer", 62.0, 60.0, 65.0,
                json.dumps(["Python", "Machine Learning", "Scikit-Learn", "Git"]),
                json.dumps(["NLP", "PyTorch", "FastAPI", "Docker", "AWS", "Transformers"]),
                json.dumps(["SQL", "R", "Tableau"]),
                "Moderate Match - Potential with Training",
                json.dumps([
                    "Profile is currently skewed towards general Data Analysis.",
                    "Needs deep learning frameworks (PyTorch/TensorFlow) and NLP production experience."
                ])
            ),
            (
                1, "Priya Patel", 3, "Cloud DevOps & Platform Engineer", 85.0, 88.0, 80.5,
                json.dumps(["AWS", "Docker", "Kubernetes", "Linux", "CI/CD", "GitHub Actions", "Python", "Bash"]),
                json.dumps(["Terraform"]),
                json.dumps(["Ansible", "Nginx", "Jenkins"]),
                "Strong Match - High Priority",
                json.dumps([
                    "Add Infrastructure-as-Code (Terraform) examples to project descriptions.",
                    "Candidate has excellent Linux and container orchestration foundation."
                ])
            )
        ]
        for uid, name, jid, jtitle, m_score, s_score, tf_score, matched, missing, bonus, verd, recs in sample_evals:
            cursor.execute(
                """INSERT INTO evaluations 
                (user_id, candidate_name, job_id, job_title, match_score, skill_score, tfidf_score, matched_skills, missing_skills, bonus_skills, verdict, recommendations)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (uid, name, jid, jtitle, m_score, s_score, tf_score, matched, missing, bonus, verd, recs)
            )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized and seeded successfully.")
