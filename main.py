from fastapi import FastAPI, Request
from datetime import datetime
import psycopg2
import os
import uvicorn

app = FastAPI()

# PostgreSQL connection from Railway environment variable
DB_URL = os.getenv("DATABASE_URL")

# Create PostgreSQL connection
def get_db_connection():
    return psycopg2.connect(DB_URL)

@app.on_event("startup")
def startup():
    """Create the remarks table if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create table for remarks
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS remarks (
        id SERIAL PRIMARY KEY,
        user_id TEXT NOT NULL,
        user_name TEXT NOT NULL,
        remark TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()

# Submit Remark Endpoint
@app.post("/submit-remark")
async def submit_remark(request: Request):
    """Submit a remark to PostgreSQL."""
    data = await request.json()

    user_id = data.get("userId")
    user_name = data.get("userName")
    remark = data.get("remark")

    if not all([user_id, user_name, remark]):
        return {"error": "Missing fields"}

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert data into PostgreSQL
    cursor.execute(
        "INSERT INTO remarks (user_id, user_name, remark) VALUES (%s, %s, %s)",
        (user_id, user_name, remark)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Remark submitted successfully"}

# Fetch All Remarks Endpoint
@app.get("/get-remarks")
def get_remarks():
    """Fetch all remarks from PostgreSQL."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM remarks")
    rows = cursor.fetchall()

    remarks = []
    for row in rows:
        remarks.append({
            "id": row[0],
            "user_id": row[1],
            "user_name": row[2],
            "remark": row[3],
            "timestamp": row[4]
        })

    cursor.close()
    conn.close()

    return {"remarks": remarks}

# Start the server
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
