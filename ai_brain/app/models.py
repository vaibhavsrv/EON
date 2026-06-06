"""
Pydantic models for EON
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class Contact(BaseModel):
    """Contact model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    preferred_app: Optional[str] = None  # sms, whatsapp, email, etc.
    frequency: int = 0  # interaction count
    last_contacted: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "phone": "9876543210",
                "email": "john@example.com",
                "preferred_app": "whatsapp"
            }
        }


class ConversationTurn(BaseModel):
    """Single turn in conversation"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None


class UserPreferences(BaseModel):
    """User preferences for the session"""
    language: str = "en"
    default_messaging_app: str = "sms"
    enable_suggestions: bool = True
    context_window: int = 10  # last N messages
    response_format: str = "structured"  # structured or natural
    
    class Config:
        json_schema_extra = {
            "example": {
                "language": "en",
                "default_messaging_app": "whatsapp",
                "enable_suggestions": True
            }
        }


class Session(BaseModel):
    """User session"""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    conversation_history: List[ConversationTurn] = []
    contacts: List[Contact] = []
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    context: Dict[str, Any] = {}  # location, time, recent_actions, etc.
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc-123",
                "user_id": "user-456",
                "preferences": {
                    "language": "en",
                    "default_messaging_app": "whatsapp"
                }
            }
        }


class ChatRequest(BaseModel):
    """Chat endpoint request"""
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Call John",
                "session_id": "optional-uuid",
                "context": {
                    "location": "home",
                    "time": "evening"
                }
            }
        }


class ToolCall(BaseModel):
    """Structured tool call"""
    tool: str
    parameters: Dict[str, Any]
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "tool": "make_call",
                "parameters": {
                    "contact": "John"
                },
                "confidence": 0.95,
                "reasoning": "User wants to call John"
            }
        }


class ActionResponse(BaseModel):
    """Structured action response"""
    action: str
    data: Dict[str, Any]
    success: bool = True
    message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "action": "call",
                "data": {
                    "contact": "9876543210"
                },
                "success": True,
                "message": "Calling John",
                "session_id": "abc-123"
            }
        }


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    error_code: str
    details: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Contact not found",
                "error_code": "CONTACT_NOT_FOUND",
                "details": {
                    "contact": "Unknown Person"
                }
            }
        }
