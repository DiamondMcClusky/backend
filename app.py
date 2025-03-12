import psycopg2
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os



app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
#connect to my specfic database
db_params = {
    "dbname": "privacy_analysis",
    "user": "postgres",
    "password": "@Diamond08",
    "host": "localhost",
    "port": "5432"
}

class PolicyURL(BaseModel):
    url: str
# Ensure static directory exists
os.makedirs("static", exist_ok=True)

  # Verify database connection
def verify_db_connection():
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")  # Simple test query
        cursor.close()
        conn.close()
        print("✅ Database connected successfully!")
    except Exception as e:
        print("❌ Database connection failed:", e)

# Function to insert data into the database
def save_policy(url: str):
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Insert URL into the database
        cursor.execute(
            "INSERT INTO healthcare_privacy_policies (url) VALUES (%s);", 
            (url,)
        )
        conn.commit()

        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print("❌ Database Insert Error:", e)
        return False


@app.post("/analyze")
async def analyze_policy(policy: PolicyURL):
    """
    Endpoint to analyze a privacy policy URL and store it in the database.
    """
    try:
        success = save_policy(policy.url)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to store URL in database")  # Fix: close the string

        return {
            "success": True,
            "data": {
                "policy_name": "Example Policy",
                "grade": "A",
                "image_path": "placeholder.png"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/image/{image_name}")
async def get_image(image_name: str):
    """
    Endpoint to serve images.
    """
    image_path = f"static/{image_name}"
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path)

if __name__ == "__main__":
    verify_db_connection()  # Test the DB connection when starting the server
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)           

