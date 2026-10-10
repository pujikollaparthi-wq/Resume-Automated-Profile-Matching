import os
import sys
import json
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, EmailStr

# Ensure local imports work properly
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.database import get_db, init_db, hash_password
from backend.parsers import extract_text_from_file, clean_extracted_text
from backend.nlp_engine import match_profile, SKILL_TAXONOMY, extract_candidate_info
from backend.sample_data import SAMPLE_RESUMES, SAMPLE_JOBS
from backend.auth import (
    create_access_token,
    get_current_user_optional,
    require_current_user,
    require_admin_or_recruiter
)

# Initialize Database
init_db()

app = FastAPI(
    title="AI Automated Profile Matching API",
    description="Intelligent ATS Resume & Job Description Matching Platform with NLP, TF-IDF, and Skill Taxonomy Analysis",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Request Models
class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: str = "candidate"  # 'candidate', 'recruiter', 'admin'

class LoginRequest(BaseModel):
    username: str
    password: str

class JobCreateRequest(BaseModel):
    title: str
    company: str
    department: str
    experience_required: str
    description: str
    required_skills: List[str]

# -------------------- AUTH ENDPOINTS --------------------

@app.post("/api/auth/register")
def register_user(req: RegisterRequest):
    conn = get_db()
    cursor = conn.cursor()
    
    # Check existing user
    cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (req.username.strip(), req.email.strip()))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username or email already registered.")
    
    valid_role = req.role if req.role in ["candidate", "recruiter", "admin"] else "candidate"
    pwd_hash = hash_password(req.password)
    
    cursor.execute(
        "INSERT INTO users (username, email, password_hash, full_name, role) VALUES (?, ?, ?, ?, ?)",
        (req.username.strip(), req.email.strip(), pwd_hash, req.full_name.strip(), valid_role)
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    
    token = create_access_token({"sub": req.username.strip(), "role": valid_role, "uid": user_id})
    return {
        "status": "success",
        "message": "User registered successfully.",
        "token": token,
        "user": {
            "id": user_id,
            "username": req.username.strip(),
            "email": req.email.strip(),
            "full_name": req.full_name.strip(),
            "role": valid_role
        }
    }

@app.post("/api/auth/login")
def login_user(req: LoginRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (req.username.strip(),))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    
    if user["password_hash"] != hash_password(req.password):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    
    token = create_access_token({"sub": user["username"], "role": user["role"], "uid": user["id"]})
    return {
        "status": "success",
        "message": "Login successful.",
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"]
        }
    }

@app.get("/api/auth/me")
def get_profile(user: Optional[dict] = Depends(get_current_user_optional)):
    if not user:
        return {"authenticated": False, "user": None}
    return {"authenticated": True, "user": user}

# -------------------- PRESETS & TAXONOMY --------------------

@app.get("/api/presets")
def get_presets():
    """Return pre-configured sample resumes and sample jobs for instant 1-click testing."""
    return {
        "sample_resumes": SAMPLE_RESUMES,
        "sample_jobs": SAMPLE_JOBS
    }

@app.get("/api/skills")
def get_skill_taxonomy():
    """Return full categorized skill dictionary."""
    return SKILL_TAXONOMY

# -------------------- JOBS ENDPOINTS --------------------

@app.get("/api/jobs")
def list_jobs():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs ORDER BY id DESC")
    jobs = []
    for row in cursor.fetchall():
        j = dict(row)
        try:
            j["required_skills"] = json.loads(j["required_skills"])
        except Exception:
            j["required_skills"] = []
        jobs.append(j)
    conn.close()
    return jobs

@app.post("/api/jobs")
def create_job(req: JobCreateRequest, user: dict = Depends(require_admin_or_recruiter)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO jobs (title, company, department, experience_required, description, required_skills, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (req.title, req.company, req.department, req.experience_required, req.description, json.dumps(req.required_skills), user["id"])
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"status": "success", "id": new_id, "message": "Job posting created successfully."}

@app.delete("/api/jobs/{job_id}")
def delete_job(job_id: int, user: dict = Depends(require_admin_or_recruiter)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Job deleted."}

# -------------------- SINGLE CANDIDATE MATCHING --------------------

@app.post("/api/match")
async def match_resume(
    resume_file: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None),
    job_id: Optional[int] = Form(None),
    job_text: Optional[str] = Form(None),
    job_title: Optional[str] = Form("Custom Role"),
    user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Match a single resume against a job description.
    Supports file upload (PDF/DOCX/TXT) or pasted resume text.
    """
    extracted_resume_text = ""
    candidate_file_name = "Pasted Resume"

    if resume_file and resume_file.filename:
        candidate_file_name = resume_file.filename
        content = await resume_file.read()
        extracted_resume_text = extract_text_from_file(candidate_file_name, content)
    elif resume_text:
        extracted_resume_text = clean_extracted_text(resume_text)
    
    if not extracted_resume_text:
        raise HTTPException(status_code=400, detail="Please provide a valid resume file or paste resume content.")

    # Determine Job Description
    target_jd_text = ""
    target_job_title = job_title or "Position"
    required_skills = []

    if job_id:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        job_row = cursor.fetchone()
        conn.close()
        if job_row:
            target_jd_text = job_row["description"]
            target_job_title = job_row["title"]
            try:
                required_skills = json.loads(job_row["required_skills"])
            except Exception:
                required_skills = []

    if not target_jd_text and job_text:
        target_jd_text = clean_extracted_text(job_text)

    if not target_jd_text:
        raise HTTPException(status_code=400, detail="Please select a target job opening or provide a job description.")

    # Run AI & NLP Matching
    result = match_profile(
        resume_text=extracted_resume_text,
        jd_text=target_jd_text,
        explicit_required_skills=required_skills
    )
    result["job_title"] = target_job_title
    result["source_filename"] = candidate_file_name

    # Save evaluation into SQLite DB
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO evaluations 
            (user_id, candidate_name, job_id, job_title, match_score, skill_score, tfidf_score, matched_skills, missing_skills, bonus_skills, verdict, recommendations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user["id"] if user else None,
                result["candidate"]["name"],
                job_id,
                target_job_title,
                result["match_score"],
                result["skill_score"],
                result["tfidf_score"],
                json.dumps([s["name"] for s in result["matched_skills"]]),
                json.dumps([s["name"] for s in result["missing_skills"]]),
                json.dumps([s["name"] for s in result["bonus_skills"]]),
                result["verdict"],
                json.dumps(result["recommendations"])
            )
        )
        conn.commit()
        result["evaluation_id"] = cursor.lastrowid
        conn.close()
    except Exception as e:
        result["evaluation_id"] = None

    return result

# -------------------- RECRUITER BATCH CANDIDATE RANKING --------------------

@app.post("/api/match/batch")
async def batch_match_candidates(
    job_id: Optional[int] = Form(None),
    job_text: Optional[str] = Form(None),
    job_title: Optional[str] = Form("Custom Role"),
    resume_files: List[UploadFile] = File([]),
    candidate_preset_keys: Optional[str] = Form(None),  # Comma-separated preset keys
    user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Recruiter Batch Mode: Evaluates multiple candidates against a single target job opening,
    ranking them on a live leaderboard sorted by Match Score.
    """
    # Determine Job Description
    target_jd_text = ""
    target_job_title = job_title or "Target Role"
    required_skills = []

    if job_id:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        job_row = cursor.fetchone()
        conn.close()
        if job_row:
            target_jd_text = job_row["description"]
            target_job_title = job_row["title"]
            try:
                required_skills = json.loads(job_row["required_skills"])
            except Exception:
                required_skills = []

    if not target_jd_text and job_text:
        target_jd_text = clean_extracted_text(job_text)

    if not target_jd_text:
        raise HTTPException(status_code=400, detail="Target job description is required for batch ranking.")

    candidates_to_process = []

    # 1. Process uploaded files
    for file in resume_files:
        if file.filename:
            content = await file.read()
            extracted = extract_text_from_file(file.filename, content)
            if extracted:
                candidates_to_process.append({
                    "source": file.filename,
                    "text": extracted
                })

    # 2. Process preset keys if requested
    if candidate_preset_keys:
        keys = [k.strip() for k in candidate_preset_keys.split(",") if k.strip()]
        for key in keys:
            if key in SAMPLE_RESUMES:
                cand = SAMPLE_RESUMES[key]
                candidates_to_process.append({
                    "source": f"{cand['name']} (Preset)",
                    "text": cand["text"]
                })

    if not candidates_to_process:
        # Default fallback: evaluate all sample candidates
        for key, cand in SAMPLE_RESUMES.items():
            candidates_to_process.append({
                "source": f"{cand['name']} ({cand['title']})",
                "text": cand["text"]
            })

    ranked_candidates = []
    for item in candidates_to_process:
        match_res = match_profile(
            resume_text=item["text"],
            jd_text=target_jd_text,
            explicit_required_skills=required_skills
        )
        match_res["source_label"] = item["source"]
        ranked_candidates.append(match_res)

    # Sort descending by match_score
    ranked_candidates.sort(key=lambda c: c["match_score"], reverse=True)

    # Assign Rank 1, 2, 3...
    for idx, c in enumerate(ranked_candidates):
        c["rank"] = idx + 1

    return {
        "job_title": target_job_title,
        "total_evaluated": len(ranked_candidates),
        "leaderboard": ranked_candidates
    }

# -------------------- ADMIN & RECRUITER METRICS --------------------

@app.get("/api/admin/metrics")
def get_admin_metrics(user: dict = Depends(require_admin_or_recruiter)):
    """
    Executive ATS Analytics Dashboard: Total evaluations, average score,
    pass/review/reject distribution, top matched vs missing skills, and recent candidate logs.
    """
    conn = get_db()
    cursor = conn.cursor()

    # Total Evaluations
    cursor.execute("SELECT COUNT(*) as total, AVG(match_score) as avg_score FROM evaluations")
    row = cursor.fetchone()
    total_evaluations = row["total"] or 0
    avg_score = round(row["avg_score"] or 0.0, 1)

    # Total registered users
    cursor.execute("SELECT COUNT(*) as user_count FROM users")
    total_users = cursor.fetchone()["user_count"]

    # Total active jobs
    cursor.execute("SELECT COUNT(*) as job_count FROM jobs")
    total_jobs = cursor.fetchone()["job_count"]

    # Verdict Distribution
    cursor.execute("SELECT verdict, COUNT(*) as count FROM evaluations GROUP BY verdict")
    verdicts = {r["verdict"]: r["count"] for r in cursor.fetchall()}

    # Recent Evaluations
    cursor.execute("SELECT * FROM evaluations ORDER BY id DESC LIMIT 15")
    recent = []
    for r in cursor.fetchall():
        item = dict(r)
        try:
            item["matched_skills"] = json.loads(item["matched_skills"])
            item["missing_skills"] = json.loads(item["missing_skills"])
            item["bonus_skills"] = json.loads(item["bonus_skills"])
            item["recommendations"] = json.loads(item["recommendations"])
        except Exception:
            pass
        recent.append(item)

    # Top Demanded Skills Analysis
    cursor.execute("SELECT required_skills FROM jobs")
    skill_counts = {}
    for r in cursor.fetchall():
        try:
            s_list = json.loads(r["required_skills"])
            for s in s_list:
                skill_counts[s] = skill_counts.get(s, 0) + 1
        except Exception:
            pass
    
    sorted_skills = sorted([{"skill": k, "count": v} for k, v in skill_counts.items()], key=lambda x: x["count"], reverse=True)

    conn.close()

    return {
        "summary": {
            "total_evaluations": total_evaluations,
            "average_match_score": avg_score,
            "total_users": total_users,
            "total_jobs": total_jobs
        },
        "verdict_distribution": verdicts,
        "top_in_demand_skills": sorted_skills[:10],
        "recent_evaluations": recent
    }

# -------------------- STATIC FRONTEND SERVING --------------------

FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def serve_index():
        index_path = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "Frontend index.html under construction"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
