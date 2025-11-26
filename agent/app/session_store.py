from pymongo import MongoClient
import os

mongo = MongoClient(os.getenv("MONGO_URI"))
db = mongo["agent_db"]
sessions = db["sessions"]

def get_or_create_session(session_id: str):
    session = sessions.find_one({"session_id": session_id})
    if session:
        return session
    
    new = {
        "session_id": session_id,
        "intent": None,
        "tool": None,
        "required_params": [],
        "collected_params": {},
        "missing_parameters": [],
        "history": []
    }
    sessions.insert_one(new)
    return new

def update_session(session_id: str, updates: dict):
    sessions.update_one({"session_id": session_id}, {"$set": updates})
