"""
Session memory management with SQLite persistence
"""

import sqlite3
import json
import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.models import Session, ConversationTurn, Contact, UserPreferences
from app.utils.logger import get_logger
from app.exceptions import MemoryError

logger = get_logger(__name__)


class SessionMemory:
    """Manages session state with SQLite persistence"""
    
    def __init__(self, db_path: str = "sessions.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_id TEXT PRIMARY KEY,
                        user_id TEXT,
                        created_at TIMESTAMP,
                        last_activity TIMESTAMP,
                        data TEXT
                    )
                """)
                
                # Contacts table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS contacts (
                        id TEXT PRIMARY KEY,
                        session_id TEXT,
                        name TEXT,
                        phone TEXT,
                        email TEXT,
                        preferred_app TEXT,
                        frequency INTEGER DEFAULT 0,
                        last_contacted TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                    )
                """)
                
                # Conversation history table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS conversation_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT,
                        role TEXT,
                        content TEXT,
                        timestamp TIMESTAMP,
                        metadata TEXT,
                        FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                    )
                """)
                
                conn.commit()
                logger.info("Database initialized successfully", extra={"context": {"db_path": self.db_path}})
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise MemoryError(f"Database initialization failed: {str(e)}")
    
    def create_session(self, user_id: Optional[str] = None) -> Session:
        """Create new session"""
        session = Session(user_id=user_id)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sessions (session_id, user_id, created_at, last_activity, data)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    session.session_id,
                    user_id,
                    session.created_at,
                    session.last_activity,
                    json.dumps(session.dict(), default=str)
                ))
                conn.commit()
            
            logger.info(f"Session created: {session.session_id}", extra={"context": {"user_id": user_id}})
            return session
        except Exception as e:
            logger.error(f"Failed to create session: {str(e)}")
            raise MemoryError(f"Failed to create session: {str(e)}")
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Retrieve session from memory"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT data FROM sessions WHERE session_id = ?", (session_id,))
                row = cursor.fetchone()
                
                if not row:
                    logger.warning(f"Session not found: {session_id}")
                    return None
                
                data = json.loads(row[0])
                session = Session(**data)
                
                # Load contacts
                contacts = self._load_contacts(session_id)
                session.contacts = contacts
                
                # Load conversation history
                history = self._load_conversation_history(session_id)
                session.conversation_history = history
                
                return session
        except Exception as e:
            logger.error(f"Failed to get session: {str(e)}")
            raise MemoryError(f"Failed to get session: {str(e)}")
    
    def update_session(self, session: Session) -> None:
        """Update session in memory"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                session.last_activity = datetime.utcnow()
                
                cursor.execute("""
                    UPDATE sessions 
                    SET last_activity = ?, data = ?
                    WHERE session_id = ?
                """, (
                    session.last_activity,
                    json.dumps(session.dict(exclude={"contacts", "conversation_history"}), default=str),
                    session.session_id
                ))
                
                conn.commit()
            logger.debug(f"Session updated: {session.session_id}")
        except Exception as e:
            logger.error(f"Failed to update session: {str(e)}")
            raise MemoryError(f"Failed to update session: {str(e)}")
    
    def add_conversation_turn(self, session_id: str, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Add message to conversation history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO conversation_history (session_id, role, content, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    session_id,
                    role,
                    content,
                    datetime.utcnow(),
                    json.dumps(metadata) if metadata else None
                ))
                conn.commit()
            logger.debug(f"Conversation turn added to {session_id}")
        except Exception as e:
            logger.error(f"Failed to add conversation turn: {str(e)}")
            raise MemoryError(f"Failed to add conversation turn: {str(e)}")
    
    def _load_conversation_history(self, session_id: str, limit: int = 50) -> List[ConversationTurn]:
        """Load conversation history from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT role, content, timestamp, metadata
                    FROM conversation_history
                    WHERE session_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (session_id, limit))
                
                turns = []
                for row in reversed(cursor.fetchall()):
                    turn = ConversationTurn(
                        role=row[0],
                        content=row[1],
                        timestamp=datetime.fromisoformat(row[2]),
                        metadata=json.loads(row[3]) if row[3] else None
                    )
                    turns.append(turn)
                return turns
        except Exception as e:
            logger.error(f"Failed to load conversation history: {str(e)}")
            return []
    
    def add_contact(self, session_id: str, contact: Contact) -> None:
        """Add contact to session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO contacts 
                    (id, session_id, name, phone, email, preferred_app, frequency, last_contacted)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    contact.id,
                    session_id,
                    contact.name,
                    contact.phone,
                    contact.email,
                    contact.preferred_app,
                    contact.frequency,
                    contact.last_contacted
                ))
                conn.commit()
            logger.debug(f"Contact added: {contact.name}")
        except Exception as e:
            logger.error(f"Failed to add contact: {str(e)}")
            raise MemoryError(f"Failed to add contact: {str(e)}")
    
    def _load_contacts(self, session_id: str) -> List[Contact]:
        """Load contacts from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, phone, email, preferred_app, frequency, last_contacted
                    FROM contacts
                    WHERE session_id = ?
                """, (session_id,))
                
                contacts = []
                for row in cursor.fetchall():
                    contact = Contact(
                        id=row[0],
                        name=row[1],
                        phone=row[2],
                        email=row[3],
                        preferred_app=row[4],
                        frequency=row[5],
                        last_contacted=datetime.fromisoformat(row[6]) if row[6] else None
                    )
                    contacts.append(contact)
                return contacts
        except Exception as e:
            logger.error(f"Failed to load contacts: {str(e)}")
            return []
    
    def get_contact_by_name(self, session_id: str, name: str) -> Optional[Contact]:
        """Find contact by name"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, phone, email, preferred_app, frequency, last_contacted
                    FROM contacts
                    WHERE session_id = ? AND LOWER(name) LIKE LOWER(?)
                    LIMIT 1
                """, (session_id, f"%{name}%"))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                return Contact(
                    id=row[0],
                    name=row[1],
                    phone=row[2],
                    email=row[3],
                    preferred_app=row[4],
                    frequency=row[5],
                    last_contacted=datetime.fromisoformat(row[6]) if row[6] else None
                )
        except Exception as e:
            logger.error(f"Failed to get contact: {str(e)}")
            return None
    
    def cleanup_old_sessions(self, days: int = 30) -> None:
        """Clean up sessions older than N days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM sessions 
                    WHERE last_activity < ?
                """, (cutoff_date,))
                deleted = cursor.rowcount
                conn.commit()
            logger.info(f"Cleaned up {deleted} old sessions")
        except Exception as e:
            logger.error(f"Failed to cleanup sessions: {str(e)}")


# Global memory instance
_memory_instance: Optional[SessionMemory] = None


def get_memory() -> SessionMemory:
    """Get or create global memory instance"""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = SessionMemory()
    return _memory_instance
