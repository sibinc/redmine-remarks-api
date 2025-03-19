from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # ✅ Import CORS middleware
import psycopg2
import os
import uvicorn

app = FastAPI()

# ✅ Enable CORS for Chrome Extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to specific origins later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PostgreSQL connection
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# ✅ Submit Remark Endpoint
@app.post("/submit-remark")
def submit_remark(userId: str, userName: str, remark: str):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Insert remark into PostgreSQL
    cur.execute(
        "INSERT INTO remarks (user_id, user_name, remark) VALUES (%s, %s, %s)", 
        (userId, userName, remark)
    )
    
    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Remark submitted successfully"}

# ✅ Fetch Remarks Endpoint
@app.get("/remarks")
def get_remarks():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT user_id, user_name, remark FROM remarks ORDER BY id DESC")
    rows = cur.fetchall()
    
    cur.close()
    conn.close()

    return [{"userId": row[0], "userName": row[1], "remark": row[2]} for row in rows]

# ✅ Start FastAPI server on port 8080
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

