from datetime import datetime
from bson import ObjectId

from .mongo_service import MongoService

mongo = MongoService()

COLLECTION = "learning_sessions"


def create_session(user_id: str, video_id: str, initial_state: dict) -> str:
    doc = {
        "user_id": user_id,
        "video_id": video_id,
        "state": initial_state,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = mongo.db[COLLECTION].insert_one(doc)
    return str(result.inserted_id)


def update_session(session_id: str, new_state: dict):
    mongo.db[COLLECTION].update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"state": new_state, "updated_at": datetime.utcnow()}}
    )


def get_session(session_id: str):
    doc = mongo.db[COLLECTION].find_one({"_id": ObjectId(session_id)})
    if doc:
        doc["id"] = str(doc["_id"])
    return doc