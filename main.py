from fastapi import FastAPI, Request
from datetime import datetime
import sqlite3

app = FastAPI()

# Connect to SQLite (local DB)
def get_db_connection():
    conn = sqlite3.connect('remarks.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create table (on startup)
@app.on_event("startup")
def startup():
    conn = get_db_connection()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS remarks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        user_name TEXT,
        remark TEXT,
        timestamp TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

# Submit Remark Endpoint
@app.post("/submit-remark")
async def submit_remark(request: Request):
    data = await request.json()

    user_id = data.get("userId")
    user_name = data.get("userName")
    remark = data.get("remark")

    if not all([user_id, user_name, remark]):
        return {"error": "Missing fields"}

    timestamp = datetime.now()

    # Insert into SQLite
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO remarks (user_id, user_name, remark, timestamp) VALUES (?, ?, ?, ?)",
        (user_id, user_name, remark, timestamp)
    )
    conn.commit()
    conn.close()

    return {"message": "Remark submitted successfully"}
