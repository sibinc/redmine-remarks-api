from fastapi import FastAPI, Request
from datetime import datetime
import sqlite3
import uvicorn

app = FastAPI()

# SQLite DB Connection
def get_db_connection():
    conn = sqlite3.connect('remarks.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create table on startup
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

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO remarks (user_id, user_name, remark, timestamp) VALUES (?, ?, ?, ?)",
        (user_id, user_name, remark, timestamp)
    )
    conn.commit()
    conn.close()

    return {"message": "Remark submitted successfully"}

@app.get("/get-remarks")
def get_remarks():
    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM remarks")
    rows = cursor.fetchall()
    conn.close()

    remarks = []
    for row in rows:
        remarks.append({
            "id": row["id"],
            "user_id": row["user_id"],
            "user_name": row["user_name"],
            "remark": row["remark"],
            "timestamp": row["timestamp"]
        })

    return {"remarks": remarks}


# Use Railway's PORT or default to 8000
if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8080))  # Default to 8000
    uvicorn.run("main:app", host="0.0.0.0", port=port)
