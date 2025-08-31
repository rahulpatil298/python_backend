import os
import requests
import smtplib
import ssl
from email.mime.text import MIMEText
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
from dotenv import dotenv_values
from pymongo import MongoClient

# --- Configuration ---
config = dotenv_values(".env")

# --- Database Connection (MongoDB) ---
# This remains for when you want to fully integrate it.
try:
    mongo_uri = f"mongodb+srv://{config.get('MONGO_DB_USER')}:{config.get('MONGO_DB_PASSWORD')}@{config.get('MONGO_DB_CLUSTER')}/?retryWrites=true&w=majority&appName={config.get('MONGO_DB_NAME')}"
    db_client = MongoClient(mongo_uri)
    db = db_client[config.get('MONGO_DB_NAME', 'your_route_db')]
    print("Successfully connected to MongoDB.")
except Exception as e:
    print(f"Could not connect to MongoDB. Running without database. Error: {e}")
    db = None

# --- Mappls API Configuration & Caching ---
MAPPIS_CLIENT_ID = config.get("MAPPIS_CLIENT_ID")
MAPPIS_CLIENT_SECRET = config.get("MAPPIS_CLIENT_SECRET")
mappls_token = None

# --- Pydantic Models ---
class UserSignup(BaseModel):
    email: str
    password: str
    userType: str
    name: str = None
    companyName: str = None

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
        'client_id': MAPPIS_CLIENT_ID,
        'client_secret': MAPPIS_CLIENT_SECRET
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


# --- NEW API Endpoints ---
@app.post("/signup")
async def signup_user(user_data: UserSignup):
    """
    Handles user registration.
    """
    print("Signup request received for:", user_data.email)
    # In a real app, you would hash the password and save the user to MongoDB here.
    return {"success": True, "message": "User created successfully!"}

@app.post("/login")
async def login_user(user_data: UserLogin):
    """
    Handles user login and returns a dummy token.
    """
    print("Login attempt for:", user_data.email)
    # In a real app, you would verify credentials against the database.
    if user_data.password == "wrong":
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"success": True, "token": "real_jwt_token_from_python"}

@app.get("/profile")
async def get_profile_data(user_type: str = "general"):
    """
    Fetches the profile data for a user.
    For the hackathon, you can change the user type via a query parameter.
    e.g., /profile?user_type=corporate or /profile?user_type=employee
    """
    print(f"Profile data requested for user type: {user_type}")
    profile = DUMMY_PROFILES.get(user_type)
    if not profile:
        raise HTTPException(status_code=404, detail="User type not found")
    return profile

# --- Existing Emergency Alert Endpoints (Unchanged) ---
def send_emergency_email(data: List[EmergencyData]):
    pass # Redacted for brevity

@app.post("/emergency_alert")
async def handle_emergency_data(emergency_list: List[EmergencyData] = Body(...)):
    await process_emergency_data(emergency_list)
    return {"message": "Emergency data processed and forwarded internally."}

@app.post("/internal_data_receiver")
async def process_emergency_data(emergency_list: List[EmergencyData]):
    send_emergency_email(emergency_list)
    return {"message": "Data received and processed successfully."}

# --- Run the server ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
