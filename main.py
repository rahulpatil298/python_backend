import os
import requests
import smtplib
import ssl
from email.mime.text import MIMEText
from typing import List

from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from dotenv import dotenv_values
from pymongo import MongoClient

# --- Configuration ---
# Load environment variables from the .env file
config = dotenv_values(".env")

# --- Database Connection (MongoDB) ---
# The user specified that they will provide instructions on how to use MongoDB later.
# This code sets up the connection but does not perform any operations.
try:
    mongo_uri = f"mongodb+srv://{config['MONGO_DB_USER']}:{config['MONGO_DB_PASSWORD']}@{config['MONGO_DB_CLUSTER']}/?retryWrites=true&w=majority&appName={config['MONGO_DB_NAME']}"
    db_client = MongoClient(mongo_uri)
    db = db_client[config['MONGO_DB_NAME']]
    print("Successfully connected to MongoDB.")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    # Consider raising an HTTPException here if the database connection is critical for startup.

# --- Models ---
# Pydantic model to validate the incoming emergency data
class EmergencyData(BaseModel):
    """
    Represents a single piece of emergency data.
    """
    emergency_type: str
    location: str
    timestamp: str

# --- FastAPI Application Setup ---
app = FastAPI(
    title="Emergency Alert Backend",
    description="A FastAPI application to handle, forward, and alert on emergency data.",
)

# --- Helper Functions ---
def send_emergency_email(data: List[EmergencyData]):
    """
    Sends an email alert containing the emergency data.
    """
    sender_email = config.get("SENDER_EMAIL")
    sender_password = config.get("SENDER_EMAIL_PASSWORD")
    receiver_email = config.get("RECEIVER_EMAIL")

    if not all([sender_email, sender_password, receiver_email]):
        print("Email credentials are not fully configured. Skipping email alert.")
        return

    # Create the email content
    subject = "EMERGENCY ALERT: New Incident Reported"
    body = "The following emergency data has been received:\n\n"
    for item in data:
        body += f"Type: {item.emergency_type}\nLocation: {item.location}\nTimestamp: {item.timestamp}\n\n"

    message = MIMEText(body)
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Send the email securely
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Emergency email alert sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

# --- API Endpoints ---
@app.post("/emergency_alert")
async def handle_emergency_data(emergency_list: List[EmergencyData] = Body(..., description="A list of emergency data objects.")):
    """
    Receives a list of emergency data and forwards it to another local API.
    """
    try:
        # Step 1: Process the data by calling the internal processing function.
        # This replaces the external requests.post call.
        await process_emergency_data(emergency_list)
        
        return {"message": "Emergency data processed and forwarded internally."}

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

# This is the new internal API endpoint to handle the data.
@app.post("/internal_data_receiver")
async def process_emergency_data(emergency_list: List[EmergencyData]):
    """
    This API receives the emergency data from the other local endpoint.
    It performs the email alert and other processing logic here.
    """
    # Step 2: Send the email alert
    send_emergency_email(emergency_list)
    
    # Step 3: (Optional) This is where you will add the MongoDB logic later.
    # For example:
    # collection = db.emergencies
    # collection.insert_many([item.dict() for item in emergency_list])
    
    return {"message": "Data received and processed successfully."}

# --- Run the server ---
# To run the server, use the command: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
