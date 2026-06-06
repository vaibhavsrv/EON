"""
Intent service for NLU, entity extraction, and multi-step planning
"""

from typing import Dict, Any, List, Optional, Tuple
from app.models import Session, Contact
from app.utils.logger import get_logger
from app.exceptions import IntentError

logger = get_logger(__name__)


class IntentService:
    """Service for intent detection, entity extraction, and multi-step planning"""
    
    # Intent keywords mapping
    INTENT_KEYWORDS = {
        "call": ["call", "ring", "dial", "phone", "reach", "contact"],
        "message": ["message", "send", "text", "sms", "whatsapp", "email", "tell"],
        "navigate": ["navigate", "go", "map", "directions", "route", "drive", "reach"],
        "open_app": ["open", "launch", "start", "app"],
        "device_control": ["turn", "toggle", "set", "control", "bluetooth", "wifi", "volume", "brightness"],
        "connectivity": ["connect", "disconnect", "enable", "disable"]
    }
    
    @staticmethod
    def detect_intent(message: str) -> str:
        """Detect primary intent from user message"""
        
        message_lower = message.lower()
        scores = {}
        
        for intent, keywords in IntentService.INTENT_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                scores[intent] = score
        
        if scores:
            detected_intent = max(scores, key=scores.get)
            logger.debug(f"Intent detected: {detected_intent} (score: {scores[detected_intent]})")
            return detected_intent
        
        logger.warning(f"Could not detect intent from: {message}")
        return "unknown"
    
    @staticmethod
    def extract_contact_entity(message: str, session: Optional[Session] = None) -> Optional[str]:
        """Extract contact name or number from message"""
        
        # Simple extraction - in production, use more sophisticated NER
        common_names = ["john", "jane", "mary", "peter", "sarah", "mike", "emma", "dad", "mom"]
        message_lower = message.lower()
        
        # Check against contacts in session
        if session and session.contacts:
            for contact in session.contacts:
                if contact.name.lower() in message_lower:
                    return contact.name
        
        # Check for phone numbers
        import re
        phone_pattern = r'[\d\s\-\+\(\)]{7,}'
        phone_match = re.search(phone_pattern, message)
        if phone_match:
            return phone_match.group().strip()
        
        # Check for common names
        for name in common_names:
            if name in message_lower:
                return name.title()
        
        # Try to extract capitalized names
        words = message.split()
        for word in words:
            if word[0].isupper() and len(word) > 2:
                return word
        
        return None
    
    @staticmethod
    def extract_destination(message: str) -> Optional[str]:
        """Extract destination from navigation intent"""
        
        keywords = ["to ", "go to ", "navigate to ", "map to ", "directions to "]
        message_lower = message.lower()
        
        for keyword in keywords:
            idx = message_lower.find(keyword)
            if idx != -1:
                # Extract text after keyword
                start = idx + len(keyword)
                return message[start:].strip().split(".")[0]
        
        # If no keyword, try to extract the last meaningful phrase
        words = message.split()
        if len(words) > 2:
            return " ".join(words[-3:])
        
        return None
    
    @staticmethod
    def extract_message_content(message: str) -> Optional[str]:
        """Extract message content from messaging intent"""
        
        keywords = [
            "message ", "send ", "text ", "tell ",
            "say ", "email ", "whatsapp ", "telegram "
        ]
        message_lower = message.lower()
        
        for keyword in keywords:
            idx = message_lower.find(keyword)
            if idx != -1:
                start = idx + len(keyword)
                remaining = message[start:].strip()
                
                # Check if there's a colon or special separator
                if ":" in remaining:
                    parts = remaining.split(":", 1)
                    return parts[1].strip()
                elif " that " in remaining:
                    parts = remaining.split(" that ", 1)
                    return parts[1].strip()
                elif " saying " in remaining:
                    parts = remaining.split(" saying ", 1)
                    return parts[1].strip()
                else:
                    return remaining
        
        return None
    
    @staticmethod
    def extract_app_name(message: str) -> Optional[str]:
        """Extract app name from open_app intent"""
        
        common_apps = [
            "gmail", "maps", "calendar", "chrome", "youtube", "spotify",
            "whatsapp", "telegram", "messenger", "instagram", "twitter",
            "settings", "photos", "notes", "clock", "weather"
        ]
        message_lower = message.lower()
        
        for app in common_apps:
            if app in message_lower:
                return app.title()
        
        # Extract capitalized words that might be app names
        words = message.split()
        for word in words:
            if word[0].isupper() and len(word) > 2:
                return word
        
        return None
    
    @staticmethod
    def check_multi_step_intent(message: str) -> bool:
        """Check if message indicates multiple steps"""
        
        multi_step_indicators = ["then", "after that", "next", "also", "and then", "followed by"]
        message_lower = message.lower()
        
        return any(indicator in message_lower for indicator in multi_step_indicators)
    
    @staticmethod
    def decompose_multi_step(message: str) -> List[str]:
        """Decompose multi-step intent into individual steps"""
        
        steps = []
        
        # Split by common separators
        import re
        parts = re.split(r'\b(then|and then|after that|next|also|,)\b', message, flags=re.IGNORECASE)
        
        for i, part in enumerate(parts):
            part = part.strip()
            if part and part.lower() not in ["then", "and then", "after that", "next", "also", ","]:
                if part:
                    steps.append(part)
        
        return steps if steps else [message]


def get_intent_service() -> IntentService:
    """Get intent service (static methods only)"""
    return IntentService()
