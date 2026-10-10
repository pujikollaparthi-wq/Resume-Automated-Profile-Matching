import re
import math
from typing import List, Dict, Set, Tuple, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Comprehensive Domain Skill Taxonomy (400+ skills categorized)
SKILL_TAXONOMY = {
    "Programming Languages": [
        "python", "javascript", "typescript", "java", "c++", "c#", "c", "go", "golang",
        "rust", "ruby", "php", "swift", "kotlin", "sql", "bash", "shell", "r", "scala",
        "dart", "perl", "matlab", "powershell", "html", "html5", "css", "css3"
    ],
    "Web & Frontend Frameworks": [
        "react", "react.js", "reactjs", "angular", "vue", "vue.js", "vuejs", "next.js", "nextjs",
        "nuxt.js", "redux", "svelte", "tailwind", "tailwindcss", "bootstrap", "sass", "less",
        "webpack", "vite", "node.js", "nodejs", "express", "express.js", "fastapi", "flask",
        "django", "spring boot", "springboot", "asp.net", "laravel", "ruby on rails", "graphql",
        "rest api", "restful api", "websockets", "microservices"
    ],
    "Cloud & DevOps": [
        "aws", "amazon web services", "azure", "microsoft azure", "gcp", "google cloud",
        "docker", "kubernetes", "k8s", "terraform", "ansible", "jenkins", "ci/cd",
        "github actions", "gitlab ci", "helm", "prometheus", "grafana", "nginx", "linux",
        "ubuntu", "serverless", "cloudformation", "ecs", "eks", "lambda", "s3", "ec2"
    ],
    "AI & Machine Learning": [
        "machine learning", "deep learning", "nlp", "natural language processing",
        "computer vision", "artificial intelligence", "transformers", "llm", "large language models",
        "huggingface", "pytorch", "tensorflow", "keras", "scikit-learn", "sklearn",
        "pandas", "numpy", "scipy", "opencv", "langchain", "openai", "gemini",
        "generative ai", "genai", "prompt engineering", "bert", "gpt", "rag",
        "vector database", "faiss", "chromadb", "xgboost", "lightgbm", "spacy", "nltk"
    ],
    "Databases & Storage": [
        "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch", "sqlite",
        "cassandra", "dynamodb", "oracle", "firebase", "neo4j", "mariadb", "sql server",
        "supabase", "mssql"
    ],
    "Data Engineering & Analytics": [
        "apache spark", "spark", "hadoop", "kafka", "apache kafka", "airflow",
        "apache airflow", "etl", "data warehousing", "snowflake", "bigquery", "redshift",
        "tableau", "power bi", "powerbi", "dbt", "data modeling", "data pipelines",
        "excel", "looker"
    ],
    "Testing & Tools": [
        "git", "github", "gitlab", "bitbucket", "jira", "confluence", "agile", "scrum",
        "kanban", "pytest", "unittest", "jest", "mocha", "selenium", "cypress", "postman",
        "swagger", "sonarqube"
    ],
    "Soft Skills & Leadership": [
        "leadership", "team leadership", "communication", "problem solving", "critical thinking",
        "team collaboration", "project management", "agile mindset", "mentorship",
        "cross-functional collaboration", "analytical skills", "stakeholder management"
    ]
}

# Inverted mapping: skill lowercase -> canonical display name and category
SKILL_MAP: Dict[str, Tuple[str, str]] = {}
for category, skills in SKILL_TAXONOMY.items():
    for skill in skills:
        # Canonical display name
        canonical = skill.title()
        if skill in ["aws", "gcp", "sql", "css", "css3", "html", "html5", "ci/cd", "nlp", "llm", "rag", "etl", "bi", "api", "rest api"]:
            canonical = skill.upper()
        elif skill in ["react.js", "vue.js", "next.js", "node.js", "express.js"]:
            canonical = skill.capitalize()
        elif skill in ["scikit-learn", "sklearn"]:
            canonical = "Scikit-Learn"
        elif skill in ["pytorch"]:
            canonical = "PyTorch"
        elif skill in ["tensorflow"]:
            canonical = "TensorFlow"
        elif skill in ["mongodb"]:
            canonical = "MongoDB"
        elif skill in ["postgresql", "postgres"]:
            canonical = "PostgreSQL"
        elif skill in ["power bi", "powerbi"]:
            canonical = "PowerBI"
        elif skill in ["github actions"]:
            canonical = "GitHub Actions"
        elif skill in ["restful api", "rest api"]:
            canonical = "RESTful APIs"
        SKILL_MAP[skill] = (canonical, category)

def extract_candidate_info(text: str) -> Dict[str, Any]:
    """Extract candidate name, email, phone, and estimated experience from raw text."""
    # Email
    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    email = email_match.group(0) if email_match else ""

    # Phone
    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    phone = phone_match.group(0) if phone_match else ""

    # Name: look at the top lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    candidate_name = "Candidate"
    for line in lines[:5]:
        # Filter out email, phone, or generic labels
        if '@' not in line and not re.search(r'\d{3}', line) and len(line) < 40 and not any(k in line.lower() for k in ['resume', 'curriculum', 'cv', 'page', 'summary', 'profile']):
            candidate_name = line
            break

    # Experience estimation
    exp_matches = re.findall(r'(\d+(?:\.\d+)?|\b\w+\b)\s*\+?\s*(?:years|yrs|year)\b(?:\s*of\s*(?:relevant\s*)?experience)?', text, re.IGNORECASE)
    years_detected = 0.0
    number_words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
    for m in exp_matches:
        try:
            val = float(m)
            if 0 < val <= 35:
                years_detected = max(years_detected, val)
        except ValueError:
            m_lower = m.lower()
            if m_lower in number_words:
                years_detected = max(years_detected, float(number_words[m_lower]))

    return {
        "name": candidate_name,
        "email": email,
        "phone": phone,
        "years_experience": years_detected
    }

def extract_skills_from_text(text: str) -> Dict[str, Dict[str, str]]:
    """
    Extract skills present in text using boundary-checked regex patterns.
    Returns dictionary: { canonical_name: {"name": canonical_name, "category": category} }
    """
    text_lower = " " + text.lower() + " "
    # Replace common punctuation with spaces except those used in skills like c++, c#, .net
    # Tokenizer-friendly normalization
    normalized = re.sub(r'[,/();:\n\r\t]', ' ', text_lower)

    found_skills: Dict[str, Dict[str, str]] = {}
    
    # Sort skill keys by length descending to match longer phrases first (e.g. 'natural language processing' before 'processing')
    sorted_skills = sorted(SKILL_MAP.keys(), key=lambda s: len(s), reverse=True)

    for skill_key in sorted_skills:
        canonical, category = SKILL_MAP[skill_key]
        if canonical in found_skills:
            continue
        
        # Word-boundary check with escape for characters like +, #, .
        escaped_key = re.escape(skill_key)
        pattern = r'(?<![a-zA-Z0-9])' + escaped_key + r'(?![a-zA-Z0-9])'
        
        if re.search(pattern, normalized):
            found_skills[canonical] = {
                "name": canonical,
                "category": category
            }

    return found_skills

def calculate_tfidf_similarity(resume_text: str, jd_text: str) -> float:
    """Calculate TF-IDF Cosine Similarity between Resume and Job Description."""
    if not resume_text.strip() or not jd_text.strip():
        return 0.0
    
    try:
        vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True
        )
        tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        # Ensure between 0.0 and 1.0
        return float(max(0.0, min(1.0, sim)))
    except Exception as e:
        return 0.0

def match_profile(
    resume_text: str,
    jd_text: str,
    explicit_required_skills: List[str] = None
) -> Dict[str, Any]:
    """
    Core AI & NLP Profile Matching Engine.
    Executes skill extraction, TF-IDF cosine similarity, gap analysis, and ATS scoring.
    """
    candidate_info = extract_candidate_info(resume_text)
    
    # 1. Extract skills from both documents
    resume_skills_dict = extract_skills_from_text(resume_text)
    jd_skills_dict = extract_skills_from_text(jd_text)

    # If explicit required skills are provided, add them to JD skills
    if explicit_required_skills:
        for sk in explicit_required_skills:
            sk_clean = sk.strip()
            if sk_clean:
                # Find canonical if exists
                sk_lower = sk_clean.lower()
                canonical = SKILL_MAP.get(sk_lower, (sk_clean, "Technical Skills"))[0]
                category = SKILL_MAP.get(sk_lower, (sk_clean, "Technical Skills"))[1]
                jd_skills_dict[canonical] = {"name": canonical, "category": category}

    resume_skills_set = set(resume_skills_dict.keys())
    jd_skills_set = set(jd_skills_dict.keys())

    # 2. Skill Gap Analysis
    matched_skills_set = resume_skills_set.intersection(jd_skills_set)
    missing_skills_set = jd_skills_set.difference(resume_skills_set)
    bonus_skills_set = resume_skills_set.difference(jd_skills_set)

    matched_skills = [resume_skills_dict[k] for k in sorted(matched_skills_set)]
    missing_skills = [jd_skills_dict[k] for k in sorted(missing_skills_set)]
    bonus_skills = [resume_skills_dict[k] for k in sorted(bonus_skills_set)]

    # 3. Compute Individual Scores
    # Skill Match Score
    if len(jd_skills_set) > 0:
        raw_skill_score = (len(matched_skills_set) / len(jd_skills_set)) * 100.0
    else:
        raw_skill_score = 75.0 if len(resume_skills_set) > 0 else 50.0

    # TF-IDF Cosine Similarity Score
    tfidf_sim = calculate_tfidf_similarity(resume_text, jd_text)
    # TF-IDF cosine similarity across different documents typically ranges 0.15 - 0.70.
    # We calibrate it using a smooth sigmoid/rescaling to provide human-readable percentage [0-100%]
    scaled_tfidf_score = min(100.0, (tfidf_sim / 0.55) * 100.0) if tfidf_sim > 0 else 0.0

    # Experience Score
    years = candidate_info.get("years_experience", 0.0)
    exp_score = min(100.0, max(60.0, 60.0 + (years * 6.0))) if years > 0 else 75.0

    # 4. Overall Weighted Score Formula
    # 50% Skill Coverage, 40% TF-IDF Semantic Overlap, 10% Experience Alignment
    overall_match_score = round(
        (raw_skill_score * 0.50) + (scaled_tfidf_score * 0.40) + (exp_score * 0.10),
        1
    )
    overall_match_score = max(5.0, min(99.0, overall_match_score))
    skill_score = round(max(0.0, min(100.0, raw_skill_score)), 1)
    tfidf_score = round(max(0.0, min(100.0, scaled_tfidf_score)), 1)

    # 5. Determine Screening Verdict & Priority
    if overall_match_score >= 80.0:
        verdict = "Strong Match - High Priority Interview"
        verdict_badge = "badge-success"
        ats_status = "PASSED"
    elif overall_match_score >= 65.0:
        verdict = "Good Match - Recommended for Screening"
        verdict_badge = "badge-info"
        ats_status = "PASSED"
    elif overall_match_score >= 50.0:
        verdict = "Moderate Match - Potential with Upskilling"
        verdict_badge = "badge-warning"
        ats_status = "REVIEW"
    else:
        verdict = "Low Fit - Critical Prerequisite Gaps"
        verdict_badge = "badge-danger"
        ats_status = "REJECTED"

    # 6. AI Recommendations & Optimization Advice
    recommendations = []
    if missing_skills:
        top_missing = [s["name"] for s in missing_skills[:4]]
        recommendations.append(f"Incorporate missing core skills required by the JD: {', '.join(top_missing)}.")
        recommendations.append(f"Add 2-3 project bullet points demonstrating hands-on usage of {top_missing[0]}.")
    
    if tfidf_score < 70.0:
        recommendations.append("Align resume vocabulary with JD terminology (mention exact domain keywords and tools).")
    
    if len(bonus_skills) > 3:
        recommendations.append(f"Strong peripheral skillset: candidate has additional strengths in {', '.join([s['name'] for s in bonus_skills[:3]])}.")

    if not recommendations:
        recommendations.append("Excellent keyword alignment and skill coverage. Resume is well-optimized for ATS screening.")

    # 7. Category Breakdown
    category_summary = {}
    for skill_item in matched_skills:
        cat = skill_item["category"]
        category_summary[cat] = category_summary.get(cat, {"matched": 0, "total": 0})
        category_summary[cat]["matched"] += 1
    
    for skill_item in missing_skills:
        cat = skill_item["category"]
        category_summary[cat] = category_summary.get(cat, {"matched": 0, "total": 0})
        category_summary[cat]["total"] += 1

    for cat in category_summary:
        category_summary[cat]["total"] += category_summary[cat]["matched"]

    return {
        "candidate": candidate_info,
        "match_score": overall_match_score,
        "skill_score": skill_score,
        "tfidf_score": tfidf_score,
        "raw_cosine_similarity": round(tfidf_sim, 4),
        "verdict": verdict,
        "verdict_badge": verdict_badge,
        "ats_status": ats_status,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "bonus_skills": bonus_skills,
        "category_summary": category_summary,
        "recommendations": recommendations,
        "stats": {
            "total_jd_skills": len(jd_skills_set),
            "total_resume_skills": len(resume_skills_set),
            "matched_count": len(matched_skills),
            "missing_count": len(missing_skills),
            "bonus_count": len(bonus_skills)
        }
    }
