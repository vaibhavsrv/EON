"""
EON AI Brain - FastAPI Backend
Main entry point with full production-ready setup
"""

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import traceback

from app.models import ChatRequest, ActionResponse, ErrorResponse
from app.utils.logger import get_logger, set_context, clear_context
from app.exceptions import EONException
from app.memory import get_memory
from app.prompts import build_system_prompt
from app.validator import validate_tool_call, validate_request
from app.services.llm_service import get_llm_service
from app.services.response_service import ResponseService
from app.services.intent_service import IntentService
from app.router import route_tool

logger = get_logger(__name__)


# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown handlers"""
    logger.info("EON Brain starting up...")
    
    # Initialize memory
    try:
        memory = get_memory()
        logger.info("Memory system initialized")
    except Exception as e:
        logger.error(f"Failed to initialize memory: {str(e)}")
    
    # Initialize LLM service
    try:
        llm_service = get_llm_service()
        logger.info("LLM service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize LLM service: {str(e)}")
    
    yield
    
    logger.info("EON Brain shutting down...")
    # Cleanup old sessions
    try:
        memory.cleanup_old_sessions(days=7)
        logger.info("Session cleanup completed")
    except Exception as e:
        logger.error(f"Failed to cleanup sessions: {str(e)}")


# Create FastAPI app
app = FastAPI(
    title="EON AI Brain",
    description="Intelligent AI assistant backend for mobile device control",
    version="1.0.0",
    lifespan=lifespan
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response logging middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log all requests and responses"""
    
    import uuid
    request_id = str(uuid.uuid4())
    set_context(request_id=request_id)
    
    logger.info(f"Request: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        logger.info(f"Response: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        raise
    finally:
        clear_context()


# Exception handlers
@app.exception_handler(EONException)
async def eon_exception_handler(request: Request, exc: EONException):
    """Handle EON exceptions"""
    logger.error(f"EON Exception: {exc.error_code} - {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=exc.to_dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {str(exc)}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "details": {"message": str(exc)}
        }
    )


# Health check endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    logger.debug("Health check")
    return {
        "status": "EON Brain Running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "components": {
            "memory": "ok",
            "llm_service": "ok",
            "router": "ok"
        }
    }


# Main chat endpoint
@app.post("/chat", response_model=ActionResponse)
async def chat(req: ChatRequest):
    """
    Main chat endpoint
    
    Accepts natural language command and returns structured action
    
    Example:
    ```
    POST /chat
    {
      "message": "Call John",
      "session_id": "optional-uuid"
    }
    ```
    """
    
    logger.info(f"Chat request: {req.message[:50]}...")
    
    try:
        # Validate request
        is_valid, validation_msg = validate_request(req.message, req.session_id)
        if not is_valid:
            logger.warning(f"Validation failed: {validation_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation_msg
            )
        
        # Get or create session
        memory = get_memory()
        
        if req.session_id:
            session = memory.get_session(req.session_id)
            if not session:
                logger.warning(f"Session not found: {req.session_id}")
                # Create new session with provided ID would require regenerating UUID
                session = memory.create_session()
        else:
            session = memory.create_session()
        
        set_context(session_id=session.session_id)
        
        # Update context if provided
        if req.context:
            session.context.update(req.context)
        
        # Add user message to history
        memory.add_conversation_turn(session.session_id, "user", req.message)
        
        # Detect intent and extract entities
        intent_service = IntentService()
        detected_intent = intent_service.detect_intent(req.message)
        logger.debug(f"Detected intent: {detected_intent}")
        
        # Generate system prompt with session context
        system_prompt = build_system_prompt(session)
        
        # Get conversation history for context
        conversation_history = [
            {
                "role": turn.role,
                "content": turn.content
            }
            for turn in session.conversation_history[-5:]  # Last 5 turns
        ]
        
        # Call LLM to generate tool call
        llm_service = get_llm_service()
        
        try:
            tool_call = llm_service.generate_tool_call(
                system_prompt=system_prompt,
                user_message=req.message,
                conversation_history=conversation_history if conversation_history else None
            )
            logger.info(f"LLM generated tool call: {tool_call.get('tool')}")
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process request"
            )
        
        # Validate tool call
        is_valid, validation_msg, error_details = validate_tool_call(tool_call)
        
        if not is_valid:
            logger.warning(f"Tool call validation failed: {validation_msg}")
            error_response = ResponseService.format_error_response(
                error=validation_msg,
                error_code="VALIDATION_ERROR",
                details=error_details,
                session_id=session.session_id
            )
            return JSONResponse(status_code=400, content=error_response)
        
        # Route tool call to action
        action_data = route_tool(tool_call)
        
        # Add assistant response to history
        memory.add_conversation_turn(
            session.session_id,
            "assistant",
            f"{tool_call.get('tool')}: {tool_call.get('parameters')}"
        )
        
        # Format response
        response = ActionResponse(
            action=action_data.get("action"),
            data=action_data.get("data"),
            success=True,
            message=f"{tool_call.get('tool')} command prepared",
            session_id=session.session_id,
            metadata={
                "tool": tool_call.get("tool"),
                "confidence": tool_call.get("confidence", 1.0),
                "intent": detected_intent
            }
        )
        
        # Update session
        memory.update_session(session)
        
        logger.info(f"Chat completed successfully: {response.action}")
        return response
    
    except HTTPException:
        raise
    except EONException as e:
        logger.error(f"EON Exception: {e.message}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=e.to_dict()
        )
    except Exception as e:
        logger.error(f"Unexpected error in chat: {str(e)}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "error_code": "INTERNAL_ERROR"
            }
        )


# Session management endpoints
@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session information"""
    
    try:
        memory = get_memory()
        session = memory.get_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session not found: {session_id}"
            )
        
        return {
            "session_id": session.session_id,
            "created_at": session.created_at,
            "last_activity": session.last_activity,
            "contacts_count": len(session.contacts),
            "message_count": len(session.conversation_history)
        }
    
    except Exception as e:
        logger.error(f"Failed to get session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve session"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False
    )
