"""
Chat History Service
Manages chat history storage, retrieval, and search functionality.
Supports both MongoDB and local JSON storage.
"""
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)


class ChatHistoryService:
    """Service for managing chat history."""
    
    def __init__(self, storage_type: str = "local"):
        """
        Initialize chat history service.
        
        Args:
            storage_type: "mongodb", "firebase", or "local"
        """
        self.storage_type = storage_type
        self.local_storage_path = Path("./data/chat_history")
        self.local_storage_path.mkdir(parents=True, exist_ok=True)
        
        # MongoDB client (lazy initialization)
        self._mongo_client = None
        self._mongo_db = None
        self._mongo_collection = None
        
        # Firebase client (lazy initialization)
        self._firebase_db = None
        
        logger.info(f"Chat history service initialized with storage type: {storage_type}")
    
    def _get_mongo_collection(self):
        """Get MongoDB collection (lazy initialization)."""
        if self._mongo_collection is None:
            try:
                from pymongo import MongoClient
                import os
                
                mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
                self._mongo_client = MongoClient(mongo_uri)
                self._mongo_db = self._mongo_client["legal_assistant"]
                self._mongo_collection = self._mongo_db["chat_history"]
                
                # Create indexes for efficient searching
                self._mongo_collection.create_index("user_id")
                self._mongo_collection.create_index("session_id")
                self._mongo_collection.create_index("timestamp")
                self._mongo_collection.create_index([("message", "text")])
                
                logger.info("MongoDB connection established")
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                raise
        
        return self._mongo_collection
    
    def _get_firebase_db(self):
        """Get Firebase database (lazy initialization)."""
        if self._firebase_db is None:
            try:
                import firebase_admin
                from firebase_admin import credentials, firestore
                import os
                
                # Initialize Firebase
                cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
                if cred_path and Path(cred_path).exists():
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                else:
                    # Use default credentials
                    firebase_admin.initialize_app()
                
                self._firebase_db = firestore.client()
                logger.info("Firebase connection established")
            except Exception as e:
                logger.error(f"Failed to connect to Firebase: {e}")
                raise
        
        return self._firebase_db
    
    async def save_message(
        self,
        user_id: str,
        session_id: str,
        message: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save a chat message and response.
        
        Args:
            user_id: User identifier
            session_id: Chat session identifier
            message: User's message
            response: Bot's response
            metadata: Additional metadata (law_type, jurisdiction, etc.)
            
        Returns:
            Message ID
        """
        message_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        chat_entry = {
            "message_id": message_id,
            "user_id": user_id,
            "session_id": session_id,
            "message": message,
            "response": response,
            "timestamp": timestamp.isoformat(),
            "metadata": metadata or {}
        }
        
        try:
            if self.storage_type == "mongodb":
                collection = self._get_mongo_collection()
                collection.insert_one(chat_entry)
                logger.info(f"Saved message to MongoDB: {message_id}")
                
            elif self.storage_type == "firebase":
                db = self._get_firebase_db()
                db.collection("chat_history").document(message_id).set(chat_entry)
                logger.info(f"Saved message to Firebase: {message_id}")
                
            else:  # local storage
                user_file = self.local_storage_path / f"{user_id}.json"
                
                # Load existing history
                if user_file.exists():
                    with open(user_file, 'r', encoding='utf-8') as f:
                        history = json.load(f)
                else:
                    history = []
                
                # Append new message
                history.append(chat_entry)
                
                # Save back to file
                with open(user_file, 'w', encoding='utf-8') as f:
                    json.dump(history, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Saved message to local storage: {message_id}")
            
            return message_id
            
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            raise
    
    async def get_session_history(
        self,
        user_id: str,
        session_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get chat history for a specific session.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            limit: Maximum number of messages to return
            
        Returns:
            List of chat messages
        """
        try:
            if self.storage_type == "mongodb":
                collection = self._get_mongo_collection()
                cursor = collection.find(
                    {"user_id": user_id, "session_id": session_id}
                ).sort("timestamp", -1).limit(limit)
                messages = list(cursor)
                # Remove MongoDB _id field
                for msg in messages:
                    msg.pop("_id", None)
                return messages[::-1]  # Reverse to chronological order
                
            elif self.storage_type == "firebase":
                db = self._get_firebase_db()
                docs = db.collection("chat_history")\
                    .where("user_id", "==", user_id)\
                    .where("session_id", "==", session_id)\
                    .order_by("timestamp", direction=firestore.Query.DESCENDING)\
                    .limit(limit)\
                    .stream()
                messages = [doc.to_dict() for doc in docs]
                return messages[::-1]  # Reverse to chronological order
                
            else:  # local storage
                user_file = self.local_storage_path / f"{user_id}.json"
                if not user_file.exists():
                    return []
                
                with open(user_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                
                # Filter by session_id
                session_messages = [
                    msg for msg in history
                    if msg.get("session_id") == session_id
                ]
                
                # Sort by timestamp and limit
                session_messages.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
                return session_messages[:limit][::-1]  # Reverse to chronological order
                
        except Exception as e:
            logger.error(f"Failed to get session history: {e}")
            return []
    
    async def get_user_sessions(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get all chat sessions for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of sessions to return
            
        Returns:
            List of session summaries
        """
        try:
            if self.storage_type == "mongodb":
                collection = self._get_mongo_collection()
                pipeline = [
                    {"$match": {"user_id": user_id}},
                    {"$sort": {"timestamp": -1}},
                    {"$group": {
                        "_id": "$session_id",
                        "last_message": {"$first": "$message"},
                        "last_timestamp": {"$first": "$timestamp"},
                        "message_count": {"$sum": 1}
                    }},
                    {"$limit": limit}
                ]
                sessions = list(collection.aggregate(pipeline))
                
                return [
                    {
                        "session_id": s["_id"],
                        "last_message": s["last_message"][:100] + "..." if len(s["last_message"]) > 100 else s["last_message"],
                        "last_timestamp": s["last_timestamp"],
                        "message_count": s["message_count"]
                    }
                    for s in sessions
                ]
                
            elif self.storage_type == "firebase":
                db = self._get_firebase_db()
                docs = db.collection("chat_history")\
                    .where("user_id", "==", user_id)\
                    .order_by("timestamp", direction=firestore.Query.DESCENDING)\
                    .stream()
                
                # Group by session
                sessions_dict = {}
                for doc in docs:
                    data = doc.to_dict()
                    session_id = data.get("session_id")
                    if session_id not in sessions_dict:
                        sessions_dict[session_id] = {
                            "session_id": session_id,
                            "last_message": data.get("message", "")[:100],
                            "last_timestamp": data.get("timestamp"),
                            "message_count": 0
                        }
                    sessions_dict[session_id]["message_count"] += 1
                
                sessions = list(sessions_dict.values())
                sessions.sort(key=lambda x: x["last_timestamp"], reverse=True)
                return sessions[:limit]
                
            else:  # local storage
                user_file = self.local_storage_path / f"{user_id}.json"
                if not user_file.exists():
                    return []
                
                with open(user_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                
                # Group by session
                sessions_dict = {}
                for msg in history:
                    session_id = msg.get("session_id")
                    if session_id not in sessions_dict:
                        sessions_dict[session_id] = {
                            "session_id": session_id,
                            "last_message": msg.get("message", "")[:100],
                            "last_timestamp": msg.get("timestamp"),
                            "message_count": 0
                        }
                    sessions_dict[session_id]["message_count"] += 1
                    # Update if this is more recent
                    if msg.get("timestamp", "") > sessions_dict[session_id]["last_timestamp"]:
                        sessions_dict[session_id]["last_message"] = msg.get("message", "")[:100]
                        sessions_dict[session_id]["last_timestamp"] = msg.get("timestamp")
                
                sessions = list(sessions_dict.values())
                sessions.sort(key=lambda x: x["last_timestamp"], reverse=True)
                return sessions[:limit]
                
        except Exception as e:
            logger.error(f"Failed to get user sessions: {e}")
            return []
    
    async def search_chat_history(
        self,
        user_id: str,
        search_query: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search through chat history.
        
        Args:
            user_id: User identifier
            search_query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching messages
        """
        try:
            search_query_lower = search_query.lower()
            
            if self.storage_type == "mongodb":
                collection = self._get_mongo_collection()
                # MongoDB text search
                cursor = collection.find(
                    {
                        "user_id": user_id,
                        "$or": [
                            {"message": {"$regex": search_query, "$options": "i"}},
                            {"response": {"$regex": search_query, "$options": "i"}}
                        ]
                    }
                ).sort("timestamp", -1).limit(limit)
                
                messages = list(cursor)
                for msg in messages:
                    msg.pop("_id", None)
                return messages
                
            elif self.storage_type == "firebase":
                db = self._get_firebase_db()
                # Firebase doesn't support full-text search natively
                # We'll fetch all user messages and filter in memory
                docs = db.collection("chat_history")\
                    .where("user_id", "==", user_id)\
                    .order_by("timestamp", direction=firestore.Query.DESCENDING)\
                    .stream()
                
                messages = []
                for doc in docs:
                    data = doc.to_dict()
                    if (search_query_lower in data.get("message", "").lower() or
                        search_query_lower in data.get("response", "").lower()):
                        messages.append(data)
                        if len(messages) >= limit:
                            break
                
                return messages
                
            else:  # local storage
                user_file = self.local_storage_path / f"{user_id}.json"
                if not user_file.exists():
                    return []
                
                with open(user_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                
                # Search in messages and responses
                matching_messages = [
                    msg for msg in history
                    if (search_query_lower in msg.get("message", "").lower() or
                        search_query_lower in msg.get("response", "").lower())
                ]
                
                # Sort by timestamp
                matching_messages.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
                return matching_messages[:limit]
                
        except Exception as e:
            logger.error(f"Failed to search chat history: {e}")
            return []
    
    async def delete_session(
        self,
        user_id: str,
        session_id: str
    ) -> bool:
        """
        Delete a chat session.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            True if successful
        """
        try:
            if self.storage_type == "mongodb":
                collection = self._get_mongo_collection()
                result = collection.delete_many({
                    "user_id": user_id,
                    "session_id": session_id
                })
                logger.info(f"Deleted {result.deleted_count} messages from MongoDB")
                return True
                
            elif self.storage_type == "firebase":
                db = self._get_firebase_db()
                docs = db.collection("chat_history")\
                    .where("user_id", "==", user_id)\
                    .where("session_id", "==", session_id)\
                    .stream()
                
                batch = db.batch()
                for doc in docs:
                    batch.delete(doc.reference)
                batch.commit()
                logger.info(f"Deleted session from Firebase: {session_id}")
                return True
                
            else:  # local storage
                user_file = self.local_storage_path / f"{user_id}.json"
                if not user_file.exists():
                    return False
                
                with open(user_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                
                # Filter out messages from this session
                filtered_history = [
                    msg for msg in history
                    if msg.get("session_id") != session_id
                ]
                
                with open(user_file, 'w', encoding='utf-8') as f:
                    json.dump(filtered_history, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Deleted session from local storage: {session_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            return False


# Singleton instance
_chat_history_service = None

def get_chat_history_service(storage_type: str = "local") -> ChatHistoryService:
    """Get or create the chat history service singleton."""
    global _chat_history_service
    if _chat_history_service is None:
        _chat_history_service = ChatHistoryService(storage_type=storage_type)
    return _chat_history_service
