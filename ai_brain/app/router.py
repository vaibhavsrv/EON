"""
Tool routing and action mapping
"""

from typing import Dict, Any
from app.utils.logger import get_logger
from app.utils.constants import *

logger = get_logger(__name__)


def route_tool(tool_call: Dict[str, Any]) -> Dict[str, Any]:
    """Route tool call to appropriate action"""
    
    tool = tool_call.get("tool", "unknown")
    parameters = tool_call.get("parameters", {})
    
    logger.debug(f"Routing tool: {tool}", extra={"context": {"tool": tool}})
    
    if tool == "make_call":
        return {
            "action": ACTION_TYPE_CALL,
            "data": {
                "contact": parameters.get("contact")
            }
        }
    
    elif tool == "send_message":
        return {
            "action": ACTION_TYPE_MESSAGE,
            "data": {
                "contact": parameters.get("contact"),
                "message": parameters.get("message"),
                "app": parameters.get("app", MESSAGING_APP_SMS)
            }
        }
    
    elif tool == "navigate":
        return {
            "action": ACTION_TYPE_NAVIGATE,
            "data": {
                "destination": parameters.get("destination")
            }
        }
    
    elif tool == "control_device":
        return {
            "action": ACTION_TYPE_DEVICE_CONTROL,
            "data": {
                "setting": parameters.get("setting"),
                "action": parameters.get("action"),
                "value": parameters.get("value")
            }
        }
    
    elif tool == "open_app":
        return {
            "action": ACTION_TYPE_OPEN_APP,
            "data": {
                "app_name": parameters.get("app_name")
            }
        }
    
    elif tool == "control_connectivity":
        return {
            "action": ACTION_TYPE_CONNECTIVITY,
            "data": {
                "connectivity_type": parameters.get("connectivity_type"),
                "action": parameters.get("action")
            }
        }
    
    else:
        logger.warning(f"Unknown tool: {tool}")
        return {
            "action": ACTION_TYPE_UNKNOWN,
            "data": {}
        }
