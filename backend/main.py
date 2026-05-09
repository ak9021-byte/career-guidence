from services.career_service import get_career_by_stream   
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.db import get_db

app = FastAPI()

# CORS--update
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
#  AUTH
# ──────────────────────────────────────────────

@app.post("/login")
def login(data: dict):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        email    = data.get("email", "").strip()
        password = data.get("password", "").strip()
        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cursor.fetchone()
        db.close()
        if user:
            return {"status": "success", "user": user}
        return {"status": "failed", "message": "Invalid credentials"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/register")
def register(data: dict):
    try:
        db = get_db()
        cursor = db.cursor()
        name     = data.get("name")
        email    = data.get("email")
        password = data.get("password")
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            return {"status": "failed", "message": "User already exists"}
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, password)
        )
        db.commit()
        db.close()
        return {"status": "success", "message": "Registered successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ──────────────────────────────────────────────
#  STUDENT
# ──────────────────────────────────────────────

@app.post("/student")
def save_student(data: dict):
    try:
        if not data.get("name"):
            return {"status": "error", "message": "Name required"}
        if not data.get("mobile"):
            return {"status": "error", "message": "Mobile required"}
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO students (user_id, name, stream, mobile, state) VALUES (%s, %s, %s, %s, %s)",
            (data.get("user_id"), data.get("name"), data.get("stream"),
             data.get("mobile"), data.get("state"))
        )
        db.commit()
        db.close()
        return {"status": "success", "message": "Student saved successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ──────────────────────────────────────────────
#  ROADMAP  –  supports all 6 stream keys
# ──────────────────────────────────────────────

STREAM_MAP = {
    "science":    "science",
    "commerce":   "commerce",
    "arts":       "arts",
    "vocational": "vocational",
    "government": "government",
    "other":      "other",
}


@app.post("/roadmap")
def roadmap(data: dict):
    raw_stream = data.get("stream", "").lower().strip()
    stream_key = STREAM_MAP.get(raw_stream, raw_stream)
    careers    = get_career_by_stream(stream_key)
    return {"status": "success", "data": careers}