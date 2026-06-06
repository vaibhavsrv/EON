"""
Structured logging system for EON
"""

import logging
import json
from datetime import datetime
from typing import Any, Optional


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        if hasattr(record, "session_id"):
            log_data["session_id"] = record.session_id
        
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        
        if hasattr(record, "context"):
            log_data["context"] = record.context
        
        return json.dumps(log_data, default=str)


class ContextFilter(logging.Filter):
    """Add contextual information to log records"""
    
    def __init__(self):
        super().__init__()
        self.context = {}
    
    def filter(self, record: logging.LogRecord) -> bool:
        for key, value in self.context.items():
            setattr(record, key, value)
        return True


class EONLogger:
    """Enhanced logger for EON with structured logging support"""
    
    _loggers = {}
    _context_filter = ContextFilter()
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get or create logger with name"""
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            logger.setLevel(logging.DEBUG)
            
            if not logger.handlers:
                handler = logging.StreamHandler()
                handler.setFormatter(JSONFormatter())
                handler.addFilter(cls._context_filter)
                logger.addHandler(handler)
            
            cls._loggers[name] = logger
        
        return cls._loggers[name]
    
    @classmethod
    def set_context(cls, **kwargs):
        """Set context variables for logging"""
        cls._context_filter.context.update(kwargs)
    
    @classmethod
    def clear_context(cls):
        """Clear context variables"""
        cls._context_filter.context.clear()


def get_logger(name: str) -> logging.Logger:
    """Convenience function to get logger"""
    return EONLogger.get_logger(name)


def set_context(**kwargs):
    """Convenience function to set logging context"""
    EONLogger.set_context(**kwargs)


def clear_context():
    """Convenience function to clear logging context"""
    EONLogger.clear_context()
