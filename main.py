from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel  # ✅ For JSON body parsing
import psycopg2
import os
import uvicorn

app = FastAPI()

# ✅ Enable CORS for Chrome Extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this later if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ PostgreSQL connection
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Create a connection to the PostgreSQL database."""
    return psycopg2.connect(DATABASE_URL)

# ✅ Pydantic model for JSON request body
class Remark(BaseModel):
    userId: str
    userName: str
    remark: str

# ✅ Submit Remark Endpoint
@app.post("/submit-remark")
def submit_remark(remark: Remark):
    """Endpoint to submit a remark."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Insert the remark into PostgreSQL
        cur.execute(
            "INSERT INTO remarks (user_id, user_name, remark) VALUES (%s, %s, %s)",
            (remark.userId, remark.userName, remark.remark)
        )

        conn.commit()
        cur.close()
        conn.close()

        return {"message": "Remark submitted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit remark: {str(e)}")

# ✅ Fetch Remarks Endpoint
@app.get("/remarks")
def get_remarks():
    """Endpoint to fetch all remarks."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Fetch all remarks
        cur.execute("SELECT user_id, user_name, remark FROM remarks ORDER BY id DESC")
        rows = cur.fetchall()

        cur.close()
        conn.close()

        return [{"userId": row[0], "userName": row[1], "remark": row[2]} for row in rows]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch remarks: {str(e)}")

# ✅ Start FastAPI server on port 8080
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

