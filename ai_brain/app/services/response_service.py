"""
Response service for formatting structured responses
"""

from typing import Dict, Any, Optional
from app.models import ActionResponse, ErrorResponse
from app.utils.logger import get_logger
from app.router import route_tool

logger = get_logger(__name__)


class ResponseService:
    """Service for formatting and validating responses"""
    
    @staticmethod
    def format_action_response(
        tool_call: Dict[str, Any],
        session_id: Optional[str] = None,
        success: bool = True,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Format a tool call into structured action response"""
        
        try:
            action_data = route_tool(tool_call)
            
            response = ActionResponse(
                action=action_data.get("action", "unknown"),
                data=action_data.get("data", {}),
                success=success,
                message=message,
                session_id=session_id,
                metadata={
                    "tool": tool_call.get("tool"),
                    "confidence": tool_call.get("confidence", 1.0)
                }
            )
            
            logger.info(f"Action response formatted: {response.action}", extra={"context": {"session_id": session_id}})
            return response.dict()
        
        except Exception as e:
            logger.error(f"Failed to format action response: {str(e)}")
            raise
    
    @staticmethod
    def format_error_response(
        error: str,
        error_code: str,
        details: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Format an error response"""
        
        response = ErrorResponse(
            error=error,
            error_code=error_code,
            details=details,
            session_id=session_id
        )
        
        logger.warning(f"Error response formatted: {error_code}", extra={"context": {"session_id": session_id}})
        return response.dict()
    
    @staticmethod
    def format_chat_response(
        action: str,
        data: Dict[str, Any],
        session_id: Optional[str] = None,
        message: Optional[str] = None,
        success: bool = True
    ) -> Dict[str, Any]:
        """Format a complete chat response"""
        
        return {
            "action": action,
            "data": data,
            "success": success,
            "message": message,
            "session_id": session_id
        }


def get_response_service() -> ResponseService:
    """Get response service (static methods only)"""
    return ResponseService()
