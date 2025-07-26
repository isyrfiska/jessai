from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import hashlib
import logging
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)

class JessAIService:
    def __init__(self, db: Session):
        self.db = db
        self.memory_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    async def process_message(self, phone: str, message: str) -> str:
        """Main message processing pipeline"""
        # Check for trained replies first
        reply = self.get_trained_reply(phone, message)
        if reply:
            return reply
        
        # Process CRM commands
        if message.startswith("crm:"):
            return self.process_crm_command(phone, message)
        
        # Process memory commands
        if message.startswith("remember:"):
            return self.process_memory_command(phone, message)
        
        # Default response
        return "How can I help you today?"
    
    # Memory System
    def update_memory(self, phone: str, key: str, value: Any) -> Dict:
        user = self._get_or_create_user(phone)
        user.memory[key] = value
        self.db.commit()
        return user.memory
    
    def get_memory(self, phone: str, key: str = None) -> Any:
        user = self.db.query(User).filter(User.phone == phone).first()
        if not user or not user.memory:
            return None
        return user.memory.get(key) if key else user.memory
    
    # CRM System
    def update_crm_field(self, phone: str, field: str, value: Any) -> Dict:
        user = self._get_or_create_user(phone)
        user.crm_data[field] = value
        self.db.commit()
        return user.crm_data
    
    def get_crm_data(self, phone: str, field: str = None) -> Any:
        user = self.db.query(User).filter(User.phone == phone).first()
        if not user or not user.crm_data:
            return None
        return user.crm_data.get(field) if field else user.crm_data
    
    # Trainable Replies
    def train_reply(self, phone: str, trigger: str, response: str) -> Dict:
        user = self._get_or_create_user(phone)
        if not user.reply_templates:
            user.reply_templates = {}
        
        trigger_hash = hashlib.md5(trigger.lower().encode()).hexdigest()
        user.reply_templates[trigger_hash] = {
            "trigger": trigger,
            "response": response,
            "usage_count": 0
        }
        self.db.commit()
        return user.reply_templates
    
    def get_trained_reply(self, phone: str, message: str) -> Optional[str]:
        user = self.db.query(User).filter(User.phone == phone).first()
        if not user or not user.reply_templates:
            return None
        
        message_lower = message.lower()
        for template in user.reply_templates.values():
            if template["trigger"].lower() in message_lower:
                template["usage_count"] += 1
                self.db.commit()
                return template["response"]
        return None
    
    # Helper methods
    def _get_or_create_user(self, phone: str) -> User:
        user = self.db.query(User).filter(User.phone == phone).first()
        if not user:
            user = User(phone=phone)
            self.db.add(user)
            self.db.commit()
        return user
    
    def process_crm_command(self, phone: str, message: str) -> str:
        try:
            _, command = message.split(":", 1)
            if "=" in command:
                field, value = [x.strip() for x in command.split("=", 1)]
                self.update_crm_field(phone, field, value)
                return f"Updated CRM: {field} = {value}"
            else:
                data = self.get_crm_data(phone, command.strip())
                return f"CRM Data: {data}" if data else "No data found"
        except Exception as e:
            logger.error(f"CRM command error: {e}")
            return "Invalid CRM command format"
    
    def process_memory_command(self, phone: str, message: str) -> str:
        try:
            _, key_value = message.split(":", 1)
            key, value = [x.strip() for x in key_value.split("=", 1)]
            self.update_memory(phone, key, value)
            return f"Remembered: {key} = {value}"
        except Exception as e:
            logger.error(f"Memory command error: {e}")
            return "Invalid memory command format"
