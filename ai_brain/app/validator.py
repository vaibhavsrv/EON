"""
Enhanced validation for tool calls
"""

from typing import Tuple, Dict, Any, Optional, List
from app.tool_registry import TOOLS
from app.utils.logger import get_logger
from app.exceptions import ValidationError, ToolNotFoundError, ParameterMissingError, ParameterTypeError

logger = get_logger(__name__)


def validate_tool_call(tool_call: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Validate a tool call structure and parameters
    Returns: (is_valid, message, error_details)
    """
    
    # Check for tool field
    if "tool" not in tool_call:
        error_msg = "Missing required field: 'tool'"
        logger.warning(error_msg)
        return False, error_msg, None
    
    tool_name = tool_call["tool"]
    
    # Find the tool definition
    selected_tool = None
    for tool in TOOLS:
        if tool["name"] == tool_name:
            selected_tool = tool
            break
    
    if selected_tool is None:
        error_msg = f"Unknown tool: '{tool_name}'"
        logger.warning(error_msg, extra={"context": {"tool": tool_name}})
        return False, error_msg, {"tool": tool_name}
    
    # Check for parameters field
    if "parameters" not in tool_call:
        error_msg = f"Missing required field: 'parameters' for tool '{tool_name}'"
        logger.warning(error_msg)
        return False, error_msg, None
    
    parameters = tool_call["parameters"]
    
    # Validate parameters is a dict
    if not isinstance(parameters, dict):
        error_msg = f"Parameters must be a dictionary, got {type(parameters).__name__}"
        logger.warning(error_msg)
        return False, error_msg, {"received_type": type(parameters).__name__}
    
    # Check required parameters
    for required_param in selected_tool["parameters"]:
        if required_param not in parameters:
            error_msg = f"Missing required parameter '{required_param}' for tool '{tool_name}'"
            logger.warning(error_msg, extra={"context": {"tool": tool_name, "parameter": required_param}})
            return False, error_msg, {"tool": tool_name, "parameter": required_param}
        
        param_value = parameters[required_param]
        if param_value is None or (isinstance(param_value, str) and not param_value.strip()):
            error_msg = f"Parameter '{required_param}' cannot be empty"
            logger.warning(error_msg)
            return False, error_msg, {"parameter": required_param}
    
    # Validate parameter types if schema is defined
    if "parameter_schemas" in selected_tool:
        for param_name, param_value in parameters.items():
            if param_name in selected_tool["parameter_schemas"]:
                schema = selected_tool["parameter_schemas"][param_name]
                
                # Check type
                if "type" in schema:
                    param_type = schema["type"]
                    
                    if param_type == "string" and not isinstance(param_value, str):
                        error_msg = f"Parameter '{param_name}' should be string, got {type(param_value).__name__}"
                        logger.warning(error_msg)
                        return False, error_msg, {
                            "parameter": param_name,
                            "expected_type": "string",
                            "received_type": type(param_value).__name__
                        }
                    
                    if param_type == "integer" and not isinstance(param_value, int):
                        error_msg = f"Parameter '{param_name}' should be integer, got {type(param_value).__name__}"
                        logger.warning(error_msg)
                        return False, error_msg, {
                            "parameter": param_name,
                            "expected_type": "integer",
                            "received_type": type(param_value).__name__
                        }
                
                # Check enum values
                if "enum" in schema:
                    allowed_values = schema["enum"]
                    if param_value not in allowed_values:
                        error_msg = f"Parameter '{param_name}' value '{param_value}' not in allowed values: {allowed_values}"
                        logger.warning(error_msg)
                        return False, error_msg, {
                            "parameter": param_name,
                            "value": param_value,
                            "allowed_values": allowed_values
                        }
                
                # Check max length
                if "max_length" in schema and isinstance(param_value, str):
                    max_len = schema["max_length"]
                    if len(param_value) > max_len:
                        error_msg = f"Parameter '{param_name}' exceeds max length of {max_len}"
                        logger.warning(error_msg)
                        return False, error_msg, {
                            "parameter": param_name,
                            "max_length": max_len,
                            "actual_length": len(param_value)
                        }
    
    logger.info(f"Tool call validation successful: {tool_name}")
    return True, "Valid", None


def validate_request(message: str, session_id: Optional[str] = None) -> Tuple[bool, str]:
    """Validate chat request"""
    
    if not message or not isinstance(message, str):
        return False, "Message must be a non-empty string"
    
    if len(message.strip()) == 0:
        return False, "Message cannot be empty or whitespace only"
    
    if len(message) > 1000:
        return False, "Message exceeds maximum length of 1000 characters"
    
    return True, "Valid"
