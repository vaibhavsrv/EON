"""
LLM service for structured interactions with GROQ
"""

import os
import json
import time
from typing import Optional, Dict, Any, List
from openai import OpenAI
from dotenv import load_dotenv
from app.utils.logger import get_logger
from app.exceptions import LLMError
from app.utils.constants import MAX_RETRIES, RETRY_BACKOFF_FACTOR, INITIAL_RETRY_DELAY

load_dotenv(dotenv_path=".env")
logger = get_logger(__name__)


class LLMService:
    """Service for LLM interactions with retry logic and error handling"""
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise LLMError("GROQ_API_KEY not found in environment variables")
        
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        self.model = "llama-3.3-70b-versatile"
    
    def generate_tool_call(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_retries: int = MAX_RETRIES
    ) -> Dict[str, Any]:
        """
        Generate structured tool call from user message
        Returns parsed JSON tool call
        """
        
        messages = []
        
        # Add system prompt
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"LLM call attempt {attempt + 1}/{max_retries}")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=1024,
                    response_format={"type": "json_object"} if os.getenv("USE_JSON_MODE") == "true" else None
                )
                
                output = response.choices[0].message.content
                
                # Clean JSON formatting
                output = output.replace("```json", "").replace("```", "").strip()
                
                # Parse JSON
                try:
                    tool_call = json.loads(output)
                    logger.info(f"LLM call successful: {tool_call.get('tool', 'unknown')}")
                    return tool_call
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from LLM: {str(e)}")
                    logger.debug(f"LLM output: {output}")
                    raise LLMError(f"Invalid JSON response from LLM: {str(e)}")
                
            except Exception as e:
                last_error = str(e)
                logger.warning(f"LLM call failed (attempt {attempt + 1}): {last_error}")
                
                if attempt < max_retries - 1:
                    wait_time = INITIAL_RETRY_DELAY * (RETRY_BACKOFF_FACTOR ** attempt)
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"LLM call failed after {max_retries} attempts")
        
        raise LLMError(f"Failed to get LLM response after {max_retries} attempts: {last_error}")
    
    def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        tool_call_result: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate natural language response based on tool call result"""
        
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
        
        if tool_call_result:
            messages.append({
                "role": "assistant",
                "content": json.dumps(tool_call_result)
            })
            messages.append({
                "role": "user",
                "content": "Generate a brief natural language response for the user based on this tool call result."
            })
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=256
            )
            
            result = response.choices[0].message.content
            logger.debug("Response generation successful")
            return result
        
        except Exception as e:
            logger.error(f"Failed to generate response: {str(e)}")
            raise LLMError(f"Failed to generate response: {str(e)}")


# Global service instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create global LLM service"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
