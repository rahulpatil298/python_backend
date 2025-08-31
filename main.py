import os
import requests
import smtplib
import ssl
from email.mime.text import MIMEText
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
from dotenv import load_dotenv  # Use load_dotenv
from pymongo import MongoClient

# --- Configuration ---
# Load environment variables from the .env file into the environment
load_dotenv()

# --- Database Connection (MongoDB) ---
# Now, we use os.getenv to reliably read the loaded variables
try:
    mongo_user = os.getenv("MONGO_DB_USER")
    mongo_password = os.getenv("MONGO_DB_PASSWORD")
    mongo_cluster = os.getenv("MONGO_DB_CLUSTER")
    mongo_dbname = os.getenv("MONGO_DB_NAME")

    if not all([mongo_user, mongo_password, mongo_cluster, mongo_dbname]):
        raise ValueError("One or more MongoDB environment variables are not set.")

    # The check above ensures mongo_dbname is a string, but we assert for type checker clarity.
    assert mongo_dbname is not None
    mongo_uri = f"mongodb+srv://{mongo_user}:{mongo_password}@{mongo_cluster}/?retryWrites=true&w=majority&appName={mongo_dbname}"
    db_client = MongoClient(mongo_uri)
    db = db_client[mongo_dbname]
    print("Successfully connected to MongoDB.")
except Exception as e:
    print(f"Could not connect to MongoDB. Running without database. Error: {e}")
    db = None

# --- Mappls API Configuration ---
MAPPLS_CLIENT_ID = os.getenv("MAPPLS_CLIENT_ID")
MAPPLS_CLIENT_SECRET = os.getenv("MAPPLS_CLIENT_SECRET")
mappls_token = None


# --- Pydantic Models ---
class UserSignup(BaseModel):
    email: str
    password: str
    userType: str
    name: Optional[str] = None
    companyName: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class EmergencyData(BaseModel):
    emergency_type: str
    location: str
    timestamp: str


# --- FastAPI Application Setup ---
app = FastAPI(
    title="Your Route Backend",
    description="Handles user authentication, profiles, and emergency alerts.",
)


# --- Mappls API Helper ---
def get_mappls_token():
    """Fetches and caches a Mappls OAuth token."""
    global mappls_token
    if mappls_token:
        return mappls_token
    
    url = "https://outpost.mappls.com/api/security/oauth/token"
    payload = {
        'grant_type': 'client_credentials',
        'client_id': MAPPLS_CLIENT_ID,
        'client_secret': MAPPLS_CLIENT_SECRET
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        mappls_token = response.json().get('access_token')
        return mappls_token
    else:
        raise HTTPException(status_code=500, detail="Could not authenticate with Mappls API.")


# --- Dummy Profile Data (matches frontend expectation) ---
DUMMY_PROFILES = {
    "general": {
      "userType": "general",
      "name": "Uthkarsh Mandloi",
      "email": "uthkarsh.m@example.com",
      "memberSince": "2025-08-15",
      "profileImage": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde"
    },
    "corporate": {
      "userType": "corporate",
      "companyName": "Your Route Logistics",
      "email": "admin@yourroute.com",
      "profileImage": "https://images.unsplash.com/photo-1599305445671-ac291c95aaa9",
      "stats": { "activeEmployees": 12, "tripsToday": 45, "totalDistance": "210 km" }
    },
    "employee": {
      "userType": "employee",
      "name": "Rajesh Kumar",
      "employeeId": "YR-EMP-007",
      "role": "Ambulance Driver",
      "profileImage": "https://images.unsplash.com/photo-1622253692010-333f2da60710",
      "currentStatus": "On Duty",
      "assignedTask": {
        "id": "SOS-1234",
        "type": "Emergency Pickup",
        "location": "Connaught Place, New Delhi",
        "eta": "8 mins"
      }
    }
}


# --- API Endpoints ---
@app.post("/signup")
async def signup_user(user_data: UserSignup):
    print("Signup request received for:", user_data.email)
    return {"success": True, "message": "User created successfully!"}

@app.post("/login")
async def login_user(user_data: UserLogin):
    print("Login attempt for:", user_data.email)
    if user_data.password == "wrong":
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"success": True, "token": "real_jwt_token_from_python"}

@app.get("/profile")
async def get_profile_data(user_type: str = "general"):
    print(f"Profile data requested for user type: {user_type}")
    profile = DUMMY_PROFILES.get(user_type)
    if not profile:
        raise HTTPException(status_code=404, detail="User type not found")
    return profile

# --- Existing Emergency Alert Endpoints ---
def send_emergency_email(data: List[EmergencyData]):
    # Redacted for brevity, logic remains the same
    pass

@app.post("/emergency_alert")
async def handle_emergency_data(emergency_list: List[EmergencyData] = Body(...)):
    await process_emergency_data(emergency_list)
    return {"message": "Emergency data processed and forwarded internally."}

@app.post("/internal_data_receiver")
async def process_emergency_data(emergency_list: List[EmergencyData]):
    send_emergency_email(emergency_list)
    return {"message": "Data received and processed successfully."}

# --- Run the server ---
# To run locally: uvicorn main:app --reload
# For deployment on services like Render, they will use a command like this.
if __name__ == "__main__":
    import uvicorn
    # Forcing host='0.0.0.0' makes it accessible on your network
    uvicorn.run(app, host="0.0.0.0", port=8000)

