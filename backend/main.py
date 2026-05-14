from services.career_service import get_career_by_stream
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.db import get_db
import psycopg2.extras

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://knowletive-frontend.vercel.app",
        "*"
    ],
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
        db     = get_db()
        cursor = db.cursor()
        email    = data.get("email", "").strip()
        password = data.get("password", "").strip()
        cursor.execute(
            "SELECT id, name, email FROM users WHERE email=%s AND password=%s",
            (email, password)
        )
        row = cursor.fetchone()
        db.close()
        if row:
            return {"status": "success", "user": {"id": row[0], "name": row[1], "email": row[2]}}
        return {"status": "failed", "message": "Invalid credentials"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/register")
def register(data: dict):
    try:
        db     = get_db()
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
        db     = get_db()
        cursor = db.cursor()
        cursor.execute(
            """INSERT INTO students
               (user_id, name, stream, mobile, state, drafted_careers, custom_careers)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                data.get("user_id"),
                data.get("name"),
                data.get("stream"),
                data.get("mobile"),
                data.get("state"),
                data.get("drafted_careers"),
                data.get("custom_careers"),
            )
        )
        db.commit()
        db.close()
        return {"status": "success", "message": "Student saved successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/students")
def get_students():
    try:
        db     = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT id, user_id, name, stream, mobile,
                   state, drafted_careers, custom_careers, created_at
            FROM students
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        students = []
        for row in rows:
            students.append({
                "id":               row[0],
                "user_id":          row[1],
                "name":             row[2],
                "stream":           row[3],
                "mobile":           row[4],
                "state":            row[5],
                "drafted_careers":  row[6],
                "custom_careers":   row[7],
                "created_at":       str(row[8])
            })
        db.close()
        return {"status": "success", "data": students}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ──────────────────────────────────────────────
#  ROADMAP
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


# ──────────────────────────────────────────────
#  COLLEGES DATA — hardcoded state + stream wise
# ──────────────────────────────────────────────

COLLEGES = {
    "maharashtra": {
        "science": [
            {"name": "IIT Bombay",                         "location": "Mumbai",     "type": "Government",    "fees": "₹2.2L/year", "ranking": "IIT #3 India"},
            {"name": "VJTI Mumbai",                        "location": "Mumbai",     "type": "Government",    "fees": "₹80K/year",  "ranking": "Top Govt Engineering"},
            {"name": "College of Engineering Pune (COEP)", "location": "Pune",       "type": "Government",    "fees": "₹1.2L/year", "ranking": "Top 10 Maharashtra"},
            {"name": "Institute of Chemical Technology",   "location": "Mumbai",     "type": "Government",    "fees": "₹90K/year",  "ranking": "Top Chemical Engg"},
            {"name": "Symbiosis Institute of Technology",  "location": "Pune",       "type": "Private",       "fees": "₹3.5L/year", "ranking": "Top Private Pune"},
            {"name": "MIT College of Engineering",         "location": "Pune",       "type": "Private",       "fees": "₹2L/year",   "ranking": "Top Private Pune"},
            {"name": "Government Medical College Nagpur",  "location": "Nagpur",     "type": "Government",    "fees": "₹50K/year",  "ranking": "Top Medical MH"},
            {"name": "BJ Medical College",                 "location": "Pune",       "type": "Government",    "fees": "₹45K/year",  "ranking": "Top Medical Pune"},
        ],
        "commerce": [
            {"name": "Sydenham College of Commerce",       "location": "Mumbai",     "type": "Government",    "fees": "₹15K/year",  "ranking": "#1 Commerce MH"},
            {"name": "HR College of Commerce",             "location": "Mumbai",     "type": "Private",       "fees": "₹35K/year",  "ranking": "Top Commerce Mumbai"},
            {"name": "Garware College of Commerce",        "location": "Pune",       "type": "Government",    "fees": "₹12K/year",  "ranking": "Top Govt Pune"},
        ],
        "arts": [
            {"name": "St. Xavier's College Mumbai",        "location": "Mumbai",     "type": "Private Aided", "fees": "₹20K/year",  "ranking": "#1 Arts Mumbai"},
            {"name": "Fergusson College",                  "location": "Pune",       "type": "Government",    "fees": "₹10K/year",  "ranking": "Top Arts Pune"},
            {"name": "Elphinstone College",                "location": "Mumbai",     "type": "Government",    "fees": "₹8K/year",   "ranking": "Top Govt Arts MH"},
        ],
        "vocational": [
            {"name": "Government Polytechnic Mumbai",      "location": "Mumbai",     "type": "Government",    "fees": "₹25K/year",  "ranking": "Top Polytechnic MH"},
            {"name": "Government Polytechnic Pune",        "location": "Pune",       "type": "Government",    "fees": "₹20K/year",  "ranking": "Top Polytechnic Pune"},
            {"name": "Government ITI Pune",                "location": "Pune",       "type": "Government",    "fees": "₹10K/year",  "ranking": "Top ITI Pune"},
        ],
        "government": [
            {"name": "Chanakya IAS Academy",               "location": "Mumbai/Pune","type": "Coaching",      "fees": "₹1.5L/year", "ranking": "Top UPSC Coaching MH"},
            {"name": "Yashada Institute",                  "location": "Pune",       "type": "Govt Training", "fees": "₹10K/year",  "ranking": "Top Govt Training MH"},
            {"name": "MPSC Maharashtra",                   "location": "Statewide",  "type": "Exam Body",     "fees": "₹500",       "ranking": "State Govt Jobs MH"},
        ],
        "other": [
            {"name": "MIT Institute of Design",            "location": "Pune",       "type": "Private",       "fees": "₹3L/year",   "ranking": "Top Design Pune"},
            {"name": "FTII Pune",                          "location": "Pune",       "type": "Government",    "fees": "₹1.2L/year", "ranking": "#1 Film Institute India"},
            {"name": "Sir J.J. Institute of Applied Art",  "location": "Mumbai",     "type": "Government",    "fees": "₹30K/year",  "ranking": "Top Art Institute MH"},
        ],
    },
    "delhi": {
        "science": [
            {"name": "IIT Delhi",                          "location": "New Delhi",  "type": "Government",    "fees": "₹2.2L/year", "ranking": "IIT #2 India"},
            {"name": "DTU Delhi",                          "location": "Delhi",      "type": "Government",    "fees": "₹1.5L/year", "ranking": "Top Engg Delhi"},
            {"name": "NSUT Delhi",                         "location": "Delhi",      "type": "Government",    "fees": "₹1.4L/year", "ranking": "Top Delhi Govt"},
            {"name": "AIIMS Delhi",                        "location": "New Delhi",  "type": "Government",    "fees": "₹1K/year",   "ranking": "#1 Medical India"},
            {"name": "Maulana Azad Medical College",       "location": "Delhi",      "type": "Government",    "fees": "₹25K/year",  "ranking": "Top Medical Delhi"},
        ],
        "commerce": [
            {"name": "SRCC Delhi",                         "location": "Delhi",      "type": "Government",    "fees": "₹18K/year",  "ranking": "#1 Commerce India"},
            {"name": "Lady Shri Ram College",              "location": "Delhi",      "type": "Government",    "fees": "₹15K/year",  "ranking": "Top Delhi University"},
            {"name": "Hindu College",                      "location": "Delhi",      "type": "Government",    "fees": "₹12K/year",  "ranking": "Top DU College"},
            {"name": "Hansraj College",                    "location": "Delhi",      "type": "Government",    "fees": "₹12K/year",  "ranking": "Top DU College"},
        ],
        "arts": [
            {"name": "Miranda House",                      "location": "Delhi",      "type": "Government",    "fees": "₹12K/year",  "ranking": "#1 College India (NIRF)"},
            {"name": "St. Stephen's College",              "location": "Delhi",      "type": "Private Aided", "fees": "₹15K/year",  "ranking": "Top Arts Delhi"},
            {"name": "Indraprastha College for Women",     "location": "Delhi",      "type": "Government",    "fees": "₹10K/year",  "ranking": "Top Women's Delhi"},
        ],
        "vocational": [
            {"name": "Government Polytechnic Delhi",       "location": "Delhi",      "type": "Government",    "fees": "₹20K/year",  "ranking": "Top Polytechnic Delhi"},
            {"name": "Delhi ITI Pusa",                     "location": "Delhi",      "type": "Government",    "fees": "₹8K/year",   "ranking": "Top ITI Delhi"},
        ],
        "government": [
            {"name": "Vajirao & Reddy Institute",          "location": "Delhi",      "type": "Coaching",      "fees": "₹1.8L/year", "ranking": "Top UPSC Delhi"},
            {"name": "Drishti IAS",                        "location": "Delhi",      "type": "Coaching",      "fees": "₹1.5L/year", "ranking": "Top UPSC Coaching"},
        ],
        "other": [
            {"name": "NIFT Delhi",                         "location": "Delhi",      "type": "Government",    "fees": "₹2L/year",   "ranking": "#1 Fashion India"},
            {"name": "National School of Drama",           "location": "Delhi",      "type": "Government",    "fees": "₹50K/year",  "ranking": "#1 Drama India"},
        ],
    },
    "karnataka": {
        "science": [
            {"name": "IISc Bangalore",                     "location": "Bangalore",  "type": "Government",    "fees": "₹35K/year",  "ranking": "#1 Research India"},
            {"name": "IIT Dharwad",                        "location": "Dharwad",    "type": "Government",    "fees": "₹2.2L/year", "ranking": "IIT Karnataka"},
            {"name": "RV College of Engineering",          "location": "Bangalore",  "type": "Private",       "fees": "₹2.5L/year", "ranking": "Top Private Engg KA"},
            {"name": "BMS College of Engineering",         "location": "Bangalore",  "type": "Private",       "fees": "₹2L/year",   "ranking": "Top Bangalore Engg"},
            {"name": "Bangalore Medical College",          "location": "Bangalore",  "type": "Government",    "fees": "₹50K/year",  "ranking": "Top Medical KA"},
        ],
        "commerce": [
            {"name": "Christ University",                  "location": "Bangalore",  "type": "Private",       "fees": "₹1.2L/year", "ranking": "Top Commerce Bangalore"},
            {"name": "St. Joseph's College of Commerce",   "location": "Bangalore",  "type": "Private Aided", "fees": "₹60K/year",  "ranking": "Top Bangalore Commerce"},
            {"name": "Jain University",                    "location": "Bangalore",  "type": "Private",       "fees": "₹1L/year",   "ranking": "Top Private KA"},
        ],
        "arts": [
            {"name": "Christ University Arts",             "location": "Bangalore",  "type": "Private",       "fees": "₹1L/year",   "ranking": "Top Arts Bangalore"},
            {"name": "Bangalore University",               "location": "Bangalore",  "type": "Government",    "fees": "₹15K/year",  "ranking": "Top Govt University KA"},
        ],
        "vocational": [
            {"name": "Government Polytechnic Bangalore",   "location": "Bangalore",  "type": "Government",    "fees": "₹18K/year",  "ranking": "Top Polytechnic KA"},
            {"name": "Government ITI Bangalore",           "location": "Bangalore",  "type": "Government",    "fees": "₹8K/year",   "ranking": "Top ITI KA"},
        ],
        "government": [
            {"name": "KPSC Karnataka",                     "location": "Statewide",  "type": "Exam Body",     "fees": "₹600",       "ranking": "State Govt Jobs KA"},
            {"name": "Brain Tree Coaching",                "location": "Bangalore",  "type": "Coaching",      "fees": "₹1.2L/year", "ranking": "Top UPSC KA"},
        ],
        "other": [
            {"name": "NIFT Bangalore",                     "location": "Bangalore",  "type": "Government",    "fees": "₹2L/year",   "ranking": "Top Fashion KA"},
            {"name": "Srishti Institute of Art",           "location": "Bangalore",  "type": "Private",       "fees": "₹2.5L/year", "ranking": "Top Design KA"},
        ],
    },
    "tamil nadu": {
        "science": [
            {"name": "IIT Madras",                         "location": "Chennai",    "type": "Government",    "fees": "₹2.2L/year", "ranking": "#1 Engineering India"},
            {"name": "Anna University",                    "location": "Chennai",    "type": "Government",    "fees": "₹80K/year",  "ranking": "Top Govt Engg TN"},
            {"name": "PSG College of Technology",          "location": "Coimbatore", "type": "Private",       "fees": "₹1.5L/year", "ranking": "Top Private TN"},
            {"name": "Madras Medical College",             "location": "Chennai",    "type": "Government",    "fees": "₹40K/year",  "ranking": "#1 Medical TN"},
        ],
        "commerce": [
            {"name": "Loyola College Chennai",             "location": "Chennai",    "type": "Private Aided", "fees": "₹25K/year",  "ranking": "Top Commerce TN"},
            {"name": "Presidency College Chennai",         "location": "Chennai",    "type": "Government",    "fees": "₹8K/year",   "ranking": "Top Govt TN"},
        ],
        "arts": [
            {"name": "Presidency College Chennai",         "location": "Chennai",    "type": "Government",    "fees": "₹8K/year",   "ranking": "Top Arts TN"},
            {"name": "Women's Christian College",          "location": "Chennai",    "type": "Private Aided", "fees": "₹20K/year",  "ranking": "Top Women's TN"},
        ],
        "vocational": [
            {"name": "Central Polytechnic Chennai",        "location": "Chennai",    "type": "Government",    "fees": "₹15K/year",  "ranking": "Top Polytechnic TN"},
            {"name": "Government ITI Chennai",             "location": "Chennai",    "type": "Government",    "fees": "₹6K/year",   "ranking": "Top ITI TN"},
        ],
        "government": [
            {"name": "TNPSC Tamil Nadu",                   "location": "Statewide",  "type": "Exam Body",     "fees": "₹150",       "ranking": "State Govt Jobs TN"},
        ],
        "other": [
            {"name": "NIFT Chennai",                       "location": "Chennai",    "type": "Government",    "fees": "₹2L/year",   "ranking": "Top Fashion TN"},
            {"name": "Madras Film Institute",              "location": "Chennai",    "type": "Government",    "fees": "₹80K/year",  "ranking": "Top Film TN"},
        ],
    },
    "gujarat": {
        "science": [
            {"name": "IIT Gandhinagar",                    "location": "Gandhinagar","type": "Government",    "fees": "₹2.2L/year", "ranking": "IIT Gujarat"},
            {"name": "NIT Surat (SVNIT)",                  "location": "Surat",      "type": "Government",    "fees": "₹1.5L/year", "ranking": "Top NIT Gujarat"},
            {"name": "LD College of Engineering",          "location": "Ahmedabad",  "type": "Government",    "fees": "₹50K/year",  "ranking": "Top Govt Engg GJ"},
            {"name": "MS University Baroda",               "location": "Vadodara",   "type": "Government",    "fees": "₹30K/year",  "ranking": "Top University GJ"},
        ],
        "commerce": [
            {"name": "HL College of Commerce",             "location": "Ahmedabad",  "type": "Government",    "fees": "₹10K/year",  "ranking": "Top Commerce GJ"},
            {"name": "GLS University",                     "location": "Ahmedabad",  "type": "Private",       "fees": "₹40K/year",  "ranking": "Top Private GJ"},
        ],
        "arts": [
            {"name": "MS University Faculty of Arts",      "location": "Vadodara",   "type": "Government",    "fees": "₹12K/year",  "ranking": "Top Arts GJ"},
            {"name": "Gujarat University",                 "location": "Ahmedabad",  "type": "Government",    "fees": "₹10K/year",  "ranking": "Top Govt University GJ"},
        ],
        "vocational": [
            {"name": "Government Polytechnic Ahmedabad",   "location": "Ahmedabad",  "type": "Government",    "fees": "₹15K/year",  "ranking": "Top Polytechnic GJ"},
            {"name": "Government ITI Ahmedabad",           "location": "Ahmedabad",  "type": "Government",    "fees": "₹5K/year",   "ranking": "Top ITI GJ"},
        ],
        "government": [
            {"name": "GPSC Gujarat",                       "location": "Statewide",  "type": "Exam Body",     "fees": "₹300",       "ranking": "State Govt Jobs GJ"},
        ],
        "other": [
            {"name": "NID Ahmedabad",                      "location": "Ahmedabad",  "type": "Government",    "fees": "₹2.5L/year", "ranking": "#1 Design Institute India"},
            {"name": "NIFT Gandhinagar",                   "location": "Gandhinagar","type": "Government",    "fees": "₹2L/year",   "ranking": "Top Fashion GJ"},
        ],
    },
    "rajasthan": {
        "science": [
            {"name": "IIT Jodhpur",                        "location": "Jodhpur",    "type": "Government",    "fees": "₹2.2L/year", "ranking": "IIT Rajasthan"},
            {"name": "BITS Pilani",                        "location": "Pilani",     "type": "Private",       "fees": "₹5L/year",   "ranking": "Top Private Engg India"},
            {"name": "MNIT Jaipur",                        "location": "Jaipur",     "type": "Government",    "fees": "₹1.5L/year", "ranking": "Top NIT RJ"},
            {"name": "SMS Medical College",                "location": "Jaipur",     "type": "Government",    "fees": "₹40K/year",  "ranking": "Top Medical RJ"},
        ],
        "commerce": [
            {"name": "University of Rajasthan Commerce",   "location": "Jaipur",     "type": "Government",    "fees": "₹8K/year",   "ranking": "Top Govt RJ"},
            {"name": "Poornima University",                "location": "Jaipur",     "type": "Private",       "fees": "₹60K/year",  "ranking": "Top Private RJ"},
        ],
        "arts": [
            {"name": "University of Rajasthan",            "location": "Jaipur",     "type": "Government",    "fees": "₹8K/year",   "ranking": "Top Arts RJ"},
        ],
        "vocational": [
            {"name": "Government Polytechnic Jaipur",      "location": "Jaipur",     "type": "Government",    "fees": "₹15K/year",  "ranking": "Top Polytechnic RJ"},
            {"name": "Government ITI Jaipur",              "location": "Jaipur",     "type": "Government",    "fees": "₹5K/year",   "ranking": "Top ITI RJ"},
        ],
        "government": [
            {"name": "RPSC Rajasthan",                     "location": "Statewide",  "type": "Exam Body",     "fees": "₹350",       "ranking": "State Govt Jobs RJ"},
        ],
        "other": [
            {"name": "NIFT Jodhpur",                       "location": "Jodhpur",    "type": "Government",    "fees": "₹2L/year",   "ranking": "Top Fashion RJ"},
        ],
    },
    "uttar pradesh": {
        "science": [
            {"name": "IIT Kanpur",                         "location": "Kanpur",     "type": "Government",    "fees": "₹2.2L/year", "ranking": "IIT #4 India"},
            {"name": "IIT BHU Varanasi",                   "location": "Varanasi",   "type": "Government",    "fees": "₹2.2L/year", "ranking": "IIT UP"},
            {"name": "MNNIT Allahabad",                    "location": "Prayagraj",  "type": "Government",    "fees": "₹1.5L/year", "ranking": "Top NIT UP"},
            {"name": "King George's Medical University",   "location": "Lucknow",    "type": "Government",    "fees": "₹50K/year",  "ranking": "Top Medical UP"},
        ],
        "commerce": [
            {"name": "Lucknow University Commerce",        "location": "Lucknow",    "type": "Government",    "fees": "₹10K/year",  "ranking": "Top Govt UP"},
            {"name": "Allahabad University",               "location": "Prayagraj",  "type": "Government",    "fees": "₹8K/year",   "ranking": "Top University UP"},
        ],
        "arts": [
            {"name": "BHU Varanasi",                       "location": "Varanasi",   "type": "Government",    "fees": "₹12K/year",  "ranking": "Top Central University"},
            {"name": "Allahabad University",               "location": "Prayagraj",  "type": "Government",    "fees": "₹8K/year",   "ranking": "Top Arts UP"},
        ],
        "vocational": [
            {"name": "Government Polytechnic Lucknow",     "location": "Lucknow",    "type": "Government",    "fees": "₹15K/year",  "ranking": "Top Polytechnic UP"},
            {"name": "Government ITI Lucknow",             "location": "Lucknow",    "type": "Government",    "fees": "₹5K/year",   "ranking": "Top ITI UP"},
        ],
        "government": [
            {"name": "UPPSC Uttar Pradesh",                "location": "Statewide",  "type": "Exam Body",     "fees": "₹200",       "ranking": "State Govt Jobs UP"},
            {"name": "Chanakya IAS Academy Lucknow",       "location": "Lucknow",    "type": "Coaching",      "fees": "₹1.2L/year", "ranking": "Top UPSC UP"},
        ],
        "other": [
            {"name": "NIFT Kanpur",                        "location": "Kanpur",     "type": "Government",    "fees": "₹2L/year",   "ranking": "Top Fashion UP"},
        ],
    },
    "west bengal": {
        "science": [
            {"name": "IIT Kharagpur",                      "location": "Kharagpur",  "type": "Government",    "fees": "₹2.2L/year", "ranking": "#1 Oldest IIT India"},
            {"name": "Jadavpur University",                "location": "Kolkata",    "type": "Government",    "fees": "₹20K/year",  "ranking": "Top Govt Engg WB"},
            {"name": "NIT Durgapur",                       "location": "Durgapur",   "type": "Government",    "fees": "₹1.5L/year", "ranking": "Top NIT WB"},
            {"name": "Medical College Kolkata",            "location": "Kolkata",    "type": "Government",    "fees": "₹40K/year",  "ranking": "Top Medical WB"},
        ],
        "commerce": [
            {"name": "St. Xavier's College Kolkata",       "location": "Kolkata",    "type": "Private Aided", "fees": "₹25K/year",  "ranking": "Top Commerce WB"},
            {"name": "Calcutta University Commerce",       "location": "Kolkata",    "type": "Government",    "fees": "₹8K/year",   "ranking": "Top Govt WB"},
        ],
        "arts": [
            {"name": "Presidency University",              "location": "Kolkata",    "type": "Government",    "fees": "₹10K/year",  "ranking": "Top Arts WB"},
            {"name": "Jadavpur University Arts",           "location": "Kolkata",    "type": "Government",    "fees": "₹15K/year",  "ranking": "Top University WB"},
        ],
        "vocational": [
            {"name": "Government Polytechnic Kolkata",     "location": "Kolkata",    "type": "Government",    "fees": "₹12K/year",  "ranking": "Top Polytechnic WB"},
        ],
        "government": [
            {"name": "WBPSC West Bengal",                  "location": "Statewide",  "type": "Exam Body",     "fees": "₹200",       "ranking": "State Govt Jobs WB"},
        ],
        "other": [
            {"name": "NIFT Kolkata",                       "location": "Kolkata",    "type": "Government",    "fees": "₹2L/year",   "ranking": "Top Fashion WB"},
            {"name": "Satyajit Ray Film Institute",        "location": "Kolkata",    "type": "Government",    "fees": "₹80K/year",  "ranking": "Top Film WB"},
        ],
    },
    "telangana": {
        "science": [
            {"name": "IIT Hyderabad",                      "location": "Hyderabad",  "type": "Government",    "fees": "₹2.2L/year", "ranking": "IIT Telangana"},
            {"name": "BITS Hyderabad",                     "location": "Hyderabad",  "type": "Private",       "fees": "₹4.5L/year", "ranking": "Top Private TS"},
            {"name": "Osmania University Engineering",     "location": "Hyderabad",  "type": "Government",    "fees": "₹40K/year",  "ranking": "Top Govt Engg TS"},
            {"name": "Nizam's Institute of Medical Sci.",  "location": "Hyderabad",  "type": "Government",    "fees": "₹50K/year",  "ranking": "Top Medical TS"},
        ],
        "commerce": [
            {"name": "Osmania University Commerce",        "location": "Hyderabad",  "type": "Government",    "fees": "₹8K/year",   "ranking": "Top Commerce TS"},
            {"name": "ICFAI University",                   "location": "Hyderabad",  "type": "Private",       "fees": "₹1.5L/year", "ranking": "Top Private TS"},
        ],
        "arts": [
            {"name": "Osmania University Arts",            "location": "Hyderabad",  "type": "Government",    "fees": "₹8K/year",   "ranking": "Top Arts TS"},
        ],
        "vocational": [
            {"name": "Government Polytechnic Hyderabad",   "location": "Hyderabad",  "type": "Government",    "fees": "₹15K/year",  "ranking": "Top Polytechnic TS"},
            {"name": "Government ITI Hyderabad",           "location": "Hyderabad",  "type": "Government",    "fees": "₹5K/year",   "ranking": "Top ITI TS"},
        ],
        "government": [
            {"name": "TSPSC Telangana",                    "location": "Statewide",  "type": "Exam Body",     "fees": "₹200",       "ranking": "State Govt Jobs TS"},
        ],
        "other": [
            {"name": "NIFT Hyderabad",                     "location": "Hyderabad",  "type": "Government",    "fees": "₹2L/year",   "ranking": "Top Fashion TS"},
        ],
    },
    "punjab": {
        "science": [
            {"name": "IIT Ropar",                          "location": "Ropar",      "type": "Government",    "fees": "₹2.2L/year", "ranking": "IIT Punjab"},
            {"name": "NIT Jalandhar",                      "location": "Jalandhar",  "type": "Government",    "fees": "₹1.5L/year", "ranking": "Top NIT PB"},
            {"name": "Thapar Institute of Engineering",    "location": "Patiala",    "type": "Private",       "fees": "₹3.5L/year", "ranking": "Top Private PB"},
            {"name": "Govt Medical College Amritsar",      "location": "Amritsar",   "type": "Government",    "fees": "₹45K/year",  "ranking": "Top Medical PB"},
        ],
        "commerce": [
            {"name": "Punjab University Commerce",         "location": "Chandigarh", "type": "Government",    "fees": "₹10K/year",  "ranking": "Top Commerce PB"},
        ],
        "arts": [
            {"name": "Panjab University",                  "location": "Chandigarh", "type": "Government",    "fees": "₹10K/year",  "ranking": "Top Arts PB"},
        ],
        "vocational": [
            {"name": "Government Polytechnic Chandigarh",  "location": "Chandigarh", "type": "Government",    "fees": "₹15K/year",  "ranking": "Top Polytechnic PB"},
            {"name": "Government ITI Ludhiana",            "location": "Ludhiana",   "type": "Government",    "fees": "₹5K/year",   "ranking": "Top ITI PB"},
        ],
        "government": [
            {"name": "PPSC Punjab",                        "location": "Statewide",  "type": "Exam Body",     "fees": "₹400",       "ranking": "State Govt Jobs PB"},
        ],
        "other": [
            {"name": "NIFT Kangra",                        "location": "Kangra",     "type": "Government",    "fees": "₹2L/year",   "ranking": "Top Fashion North"},
        ],
    },
}

TOP_NATIONAL = {
    "science": [
        {"name": "IIT Madras",     "location": "Chennai, TN",   "type": "Government", "fees": "₹2.2L/year", "ranking": "#1 Engineering India"},
        {"name": "IIT Delhi",      "location": "New Delhi",     "type": "Government", "fees": "₹2.2L/year", "ranking": "#2 India"},
        {"name": "IIT Bombay",     "location": "Mumbai, MH",    "type": "Government", "fees": "₹2.2L/year", "ranking": "#3 India"},
        {"name": "IISc Bangalore", "location": "Bangalore, KA", "type": "Government", "fees": "₹35K/year",  "ranking": "#1 Research India"},
        {"name": "AIIMS Delhi",    "location": "New Delhi",     "type": "Government", "fees": "₹1K/year",   "ranking": "#1 Medical India"},
        {"name": "BITS Pilani",    "location": "Pilani, RJ",    "type": "Private",    "fees": "₹5L/year",   "ranking": "Top Private Engg"},
    ],
    "commerce": [
        {"name": "SRCC Delhi",        "location": "New Delhi",    "type": "Government",    "fees": "₹18K/year",  "ranking": "#1 Commerce India"},
        {"name": "Sydenham College",  "location": "Mumbai, MH",   "type": "Government",    "fees": "₹15K/year",  "ranking": "#2 Commerce India"},
        {"name": "Christ University", "location": "Bangalore, KA","type": "Private",        "fees": "₹1.2L/year", "ranking": "Top Private Commerce"},
        {"name": "Loyola College",    "location": "Chennai, TN",  "type": "Private Aided", "fees": "₹25K/year",  "ranking": "Top South Commerce"},
    ],
    "arts": [
        {"name": "Miranda House",       "location": "New Delhi",  "type": "Government",    "fees": "₹12K/year", "ranking": "#1 College India (NIRF)"},
        {"name": "St. Stephen's",       "location": "New Delhi",  "type": "Private Aided", "fees": "₹15K/year", "ranking": "Top Arts India"},
        {"name": "Presidency Kolkata",  "location": "Kolkata, WB","type": "Government",    "fees": "₹10K/year", "ranking": "Top Arts East India"},
        {"name": "St. Xavier's Mumbai", "location": "Mumbai, MH", "type": "Private Aided", "fees": "₹20K/year", "ranking": "Top Arts Mumbai"},
    ],
    "government": [
        {"name": "Vajirao & Reddy", "location": "New Delhi", "type": "Coaching", "fees": "₹1.8L/year", "ranking": "Top UPSC Coaching"},
        {"name": "Chanakya IAS",    "location": "Pan India", "type": "Coaching", "fees": "₹1.5L/year", "ranking": "Top UPSC Coaching"},
        {"name": "Drishti IAS",     "location": "Pan India", "type": "Coaching", "fees": "₹1.2L/year", "ranking": "Top UPSC Coaching"},
    ],
    "vocational": [
        {"name": "Govt ITI Mumbai",        "location": "Mumbai, MH",  "type": "Government", "fees": "₹15K/year", "ranking": "Top ITI West India"},
        {"name": "Govt Polytechnic Delhi", "location": "New Delhi",   "type": "Government", "fees": "₹20K/year", "ranking": "Top Polytechnic North"},
        {"name": "Central Poly Chennai",   "location": "Chennai, TN", "type": "Government", "fees": "₹15K/year", "ranking": "Top Polytechnic South"},
    ],
    "other": [
        {"name": "NID Ahmedabad",         "location": "Ahmedabad, GJ","type": "Government", "fees": "₹2.5L/year", "ranking": "#1 Design India"},
        {"name": "NIFT Delhi",            "location": "New Delhi",    "type": "Government", "fees": "₹2L/year",   "ranking": "#1 Fashion India"},
        {"name": "FTII Pune",             "location": "Pune, MH",     "type": "Government", "fees": "₹1.2L/year", "ranking": "#1 Film Institute India"},
        {"name": "National School Drama", "location": "New Delhi",    "type": "Government", "fees": "₹50K/year",  "ranking": "#1 Drama India"},
    ],
}


# ──────────────────────────────────────────────
#  CHAT HELPER FUNCTIONS
# ──────────────────────────────────────────────

def handle_college_query(question: str, state: str, stream: str) -> dict:
    colleges   = []
    source     = ""
    stream_key = stream.lower().strip() if stream else ""
    if stream_key not in ["science","commerce","arts","vocational","government","other"]:
        stream_key = ""

    if state:
        state_data = COLLEGES.get(state, {})
        if state_data:
            if stream_key and stream_key in state_data:
                colleges = state_data[stream_key]
                source   = f"{state.title()} — {stream_key.title()} stream"
            elif not stream_key:
                for s, cols in state_data.items():
                    colleges.extend(cols[:2])
                source = f"{state.title()} — All streams"
            else:
                colleges = TOP_NATIONAL.get(stream_key, [])
                source   = f"Top National — {stream_key.title()} (no state-specific data)"
        else:
            if stream_key:
                colleges = TOP_NATIONAL.get(stream_key, [])
            else:
                for s, cols in TOP_NATIONAL.items():
                    colleges.extend(cols[:1])
            source = f"Top National (state '{state.title()}' not in our database yet)"
    else:
        if stream_key:
            colleges = TOP_NATIONAL.get(stream_key, [])
            source   = f"Top National — {stream_key.title()} stream"
        else:
            for s, cols in TOP_NATIONAL.items():
                colleges.extend(cols[:2])
            source = "Top National Colleges — All Streams"

    if not colleges:
        return {
            "status":  "success",
            "answer":  "Sorry, no college data found. I currently cover: Maharashtra, Delhi, Karnataka, Tamil Nadu, Gujarat, Rajasthan, UP, Punjab, West Bengal, Telangana.",
            "careers": []
        }

    lines = [f"🏫 **{source}:**\n"]
    for i, c in enumerate(colleges[:7], 1):
        lines.append(
            f"{i}. **{c['name']}**\n"
            f"   📍 {c['location']}  |  🏛️ {c['type']}\n"
            f"   💳 Fees: {c['fees']}  |  ⭐ {c['ranking']}"
        )
    if not state:
        lines.append("\n💡 *Tip: Mention your state for more specific results!*")

    return {"status": "success", "answer": "\n\n".join(lines), "careers": []}


def handle_career_query(question: str, state: str, stream: str) -> dict:
    all_streams       = ["science","commerce","arts","vocational","government","other"]
    streams_to_search = [stream] if stream and stream in all_streams else all_streams

    matched = []
    for s in streams_to_search:
        careers = get_career_by_stream(s)
        for c in careers:
            score  = 0
            course = str(c.get("course",  "")).lower()
            jobs   = str(c.get("jobs",    "")).lower()
            exam   = str(c.get("exam",    "")).lower()
            salary = str(c.get("salary",  "")).lower()
            future = str(c.get("future",  "")).lower()
            for word in question.split():
                if len(word) < 3: continue
                if word in course:  score += 3
                if word in jobs:    score += 2
                if word in exam:    score += 2
                if word in salary:  score += 1
                if word in future:  score += 1
            if score > 0:
                matched.append({**c, "_score": score, "_stream": s})

    matched.sort(key=lambda x: x["_score"], reverse=True)
    top = matched[:8]

    if not top:
        return {
            "status":  "success",
            "answer":  "I couldn't find data for your question in our database.\n\nTry asking about:\n• Salary after a course\n• Entrance exams\n• Job roles\n• Course fees\n• Best colleges in your state",
            "careers": []
        }

    return {
        "status":  "success",
        "answer":  build_answer(question, top, state),
        "careers": top[:5]
    }


def build_answer(question: str, careers: list, state: str) -> str:
    q = question.lower()

    if any(w in q for w in ["salary","earn","income","pay","lpa","package"]):
        lines = ["💰 **Salary Information from our database:**\n"]
        for c in careers[:5]:
            if c.get("salary") and c["salary"] not in ("nan",""):
                lines.append(f"• **{c['course']}** → {c['salary']}")
        return "\n".join(lines) if len(lines) > 1 else "Salary data not found for this query."

    if any(w in q for w in ["exam","entrance","test","upsc","jee","neet","gate"]):
        lines = ["📝 **Entrance Exams from our database:**\n"]
        for c in careers[:5]:
            if c.get("exam") and c["exam"] not in ("nan",""):
                lines.append(f"• **{c['course']}** → {c['exam']}")
        return "\n".join(lines) if len(lines) > 1 else "Exam data not found for this query."

    if any(w in q for w in ["fee","cost","fees","expensive","cheap","afford"]):
        lines = ["💳 **Course Fees from our database:**\n"]
        for c in careers[:5]:
            if c.get("course_fee") and c["course_fee"] not in ("nan",""):
                lines.append(f"• **{c['course']}** → {c['course_fee']}")
        return "\n".join(lines) if len(lines) > 1 else "Fee data not found for this query."

    if any(w in q for w in ["job","work","career","role","scope","future"]):
        lines = ["💼 **Job Roles from our database:**\n"]
        for c in careers[:5]:
            if c.get("jobs") and c["jobs"] not in ("nan",""):
                lines.append(f"• **{c['course']}** → {c['jobs']}")
        return "\n".join(lines) if len(lines) > 1 else "Job data not found for this query."

    if any(w in q for w in ["duration","year","years","long","time","period"]):
        lines = ["⏱️ **Course Duration from our database:**\n"]
        for c in careers[:5]:
            if c.get("duration") and c["duration"] not in ("nan",""):
                lines.append(f"• **{c['course']}** → {c['duration']}")
        return "\n".join(lines) if len(lines) > 1 else "Duration data not found for this query."

    lines = [f"🎓 **Found {len(careers)} matching careers:**\n"]
    for i, c in enumerate(careers[:6], 1):
        line = f"{i}. **{c['course']}**"
        if c.get("duration") and c["duration"] not in ("nan",""):
            line += f" | {c['duration']}"
        if c.get("salary") and c["salary"] not in ("nan",""):
            line += f" | {c['salary']}"
        lines.append(line)
    lines.append("\n📍 Data from Knowletive career database.")
    return "\n".join(lines)


# ──────────────────────────────────────────────
#  CHAT ENDPOINT
# ──────────────────────────────────────────────

@app.post("/chat")
def chat(data: dict):
    try:
        question = data.get("question", "").lower().strip()
        state    = data.get("state",    "").lower().strip()
        stream   = data.get("stream",   "").lower().strip()

        college_keywords = [
            "college", "university", "institute", "admission",
            "best college", "top college", "where to study",
            "which college", "good college", "colleges in"
        ]
        is_college_question = any(kw in question for kw in college_keywords)

        if is_college_question:
            return handle_college_query(question, state, stream)
        else:
            return handle_career_query(question, state, stream)

    except Exception as e:
        return {"status": "error", "answer": f"Error: {str(e)}", "careers": []}