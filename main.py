from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2

# ✅ Update this with your actual working DB password
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "resumematcher",
    "user": "postgres",
    "password": "yourpassword"  # <-- Replace this!
}

app = FastAPI()

# ✅ CORS: allow frontend running on Live Server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Resume Matcher API is running"}

@app.get("/resumes")
def get_resumes():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            SELECT resumes.id, users.name, resumes.summary
            FROM resumes
            JOIN users ON resumes.user_id = users.id
        """)
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception as e:
        return {"error": str(e)}

@app.get("/match/{resume_id}")
def match_jobs(resume_id: int):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            SELECT
                jobs.id,
                jobs.title,
                jobs.company,
                jobs.location,
                COUNT(*) AS score,
                jobs.created_at
            FROM jobs
            JOIN job_skills ON jobs.id = job_skills.job_id
            JOIN resume_skills ON job_skills.skill_id = resume_skills.skill_id
            WHERE resume_skills.resume_id = %s
            GROUP BY jobs.id
            ORDER BY score DESC
        """, (resume_id,))
        matches = cur.fetchall()
        conn.close()
        return matches
    except Exception as e:
        return {"error": str(e)}
