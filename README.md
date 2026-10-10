# AI Automated Resume & Job Description Profile Matcher 🚀

> **Intelligent ATS Resume Screener, Candidate Ranking System, and Skill Analytics Platform** powered by FastAPI, Natural Language Processing (NLP), TF-IDF Cosine Similarity, and dynamic multi-dimensional Skill Taxonomy.

---

## 🌟 Key Features

- **📄 Multi-Format Resume Parsing**: Extract raw text and structural content from **PDF**, **DOCX**, and plain text files.
- **🧠 400+ Skill Taxonomy Extraction**: Named Entity Recognition (NER) pipeline targeting 400+ technical, cloud, AI/ML, framework, database, and soft skills.
- **📐 TF-IDF & Cosine Similarity Engine**: Calculates term frequency-inverse document frequency vector representations to evaluate semantic alignment between resumes and job descriptions.
- **📊 Multi-Factor Candidate Scoring**: Weighted match algorithm combining skill coverage (50%), TF-IDF vector similarity (40%), and experience alignment (10%).
- **🏆 Recruiter Batch Leaderboard**: Screen multiple applicant resumes against a single job opening in parallel and instantly view ranked leaderboard results.
- **📈 Executive Admin Dashboard**: Comprehensive analytics on average match scores, verdict distributions, candidate evaluation logs, and top in-demand technical skills.
- **🔐 JWT Authentication & RBAC**: Role-based access control supporting **Candidate**, **Recruiter**, and **Admin** user types with instant 1-click demo logins.
- **🎨 Glassmorphic Premium Dark UI**: Modern responsive web application built with HTML5, CSS3 CSS Variables, SVG animated score dials, and interactive filtering.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Backend API** | Python 3.10+, FastAPI, Uvicorn, Pydantic |
| **NLP & Vectorization** | Scikit-Learn (TF-IDF Vectorizer), NumPy, Custom Regex NER Pipeline |
| **Document Parsing** | PyPDF2, `python-docx` |
| **Database** | SQLite3 (Zero-config embedded relational DB with user/eval/job tables) |
| **Frontend UI** | HTML5, Vanilla CSS3 (Custom Design System), Modern ES6+ JavaScript |
| **Security** | SHA-256 Password Hashing, JWT Token Authorization |

---

## 🚀 Quick Start & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/pujikollaparthi/resume-matcher-ai.git
cd resume-matcher-ai
```

### 2. Create Virtual Environment & Install Dependencies
```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Application Server
```bash
python backend/main.py
```
Or with Uvicorn CLI directly:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access the Web Application
Open your web browser and navigate to:
- **Web App UI**: `http://localhost:8000`
- **Interactive API Documentation (Swagger UI)**: `http://localhost:8000/docs`
- **ReDoc API Documentation**: `http://localhost:8000/redoc`

---

## 📐 Scoring Formula & NLP Architecture

$$\text{Match Score} = (0.50 \times \text{Skill Coverage Score}) + (0.40 \times \text{TF-IDF Cosine Similarity}) + (0.10 \times \text{Experience Match})$$

```
+-------------------+      +-----------------------+
|  Candidate Resume |      |    Job Description    |
|   (PDF/DOCX/TXT)  |      |      Requirement      |
+---------+---------+      +-----------+-----------+
          |                            |
          v                            v
  +-------+----------------------------+-------+
  |    NLP Text Preprocessing & Cleaning       |
  +-------------------+------------------------+
                      |
        +-------------+-------------+
        |                           |
        v                           v
+-------+---------------+   +-------+---------------+
| 400+ Skill Extraction |   | TF-IDF N-gram Vectors |
| (Regex NER Pipeline)  |   | & Cosine Similarity   |
+-------+---------------+   +-------+---------------+
        |                           |
        +-------------+-------------+
                      |
                      v
       +--------------+--------------+
       | Weighted Scoring Formula    |
       | & Skill Gap Identification  |
       +--------------+--------------+
                      |
                      v
       +--------------+--------------+
       | Final Match Score & Verdict |
       | (Pass / Review / Reject)    |
       +-----------------------------+
```

---

## 📂 Project Folder Structure

```
resume-matcher-ai/
├── backend/
│   ├── __init__.py
│   ├── auth.py              # JWT authentication & password hashing
│   ├── database.py          # SQLite schema initialization & queries
│   ├── main.py              # FastAPI endpoints & route definitions
│   ├── nlp_engine.py        # TF-IDF, skill extraction & scoring engine
│   ├── parsers.py           # PDF and DOCX file text extraction
│   └── sample_data.py       # Pre-configured sample resumes & jobs
├── data/
│   └── app.db               # SQLite database file
├── frontend/
│   ├── app.js               # Frontend interactive logic & API calls
│   ├── index.css            # Dark mode glassmorphic CSS design system
│   └── index.html           # Single Page Application (SPA) structure
├── .gitignore               # Git ignore rules
├── README.md                # Project documentation
└── requirements.txt         # Python package dependencies
```

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
