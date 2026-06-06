"""
Tool registry for EON
Defines all available tools with their schemas and parameter requirements
"""

TOOLS = [
    {
        "name": "make_call",
        "description": "Call a contact by phone number or name",
        "parameters": ["contact"],
        "parameter_schemas": {
            "contact": {
                "type": "string",
                "description": "Contact name or phone number",
                "required": True
            }
        },
        "examples": [
            {
                "input": {"contact": "John"},
                "expected_output": {"action": "call", "data": {"contact": "9876543210"}}
            }
        ]
    },
    {
        "name": "send_message",
        "description": "Send a message to a contact via SMS, WhatsApp, Email, or Telegram",
        "parameters": ["contact", "message"],
        "parameter_schemas": {
            "contact": {
                "type": "string",
                "description": "Contact name or phone number/email",
                "required": True
            },
            "message": {
                "type": "string",
                "description": "Message content",
                "required": True,
                "max_length": 1000
            },
            "app": {
                "type": "string",
                "description": "App to use (sms, whatsapp, email, telegram)",
                "required": False,
                "default": "sms"
            }
        },
        "examples": [
            {
                "input": {"contact": "John", "message": "Hello", "app": "whatsapp"},
                "expected_output": {"action": "message", "data": {"contact": "9876543210", "message": "Hello", "app": "whatsapp"}}
            }
        ]
    },
    {
        "name": "navigate",
        "description": "Open navigation to a destination on Google Maps",
        "parameters": ["destination"],
        "parameter_schemas": {
            "destination": {
                "type": "string",
                "description": "Location name or address",
                "required": True
            }
        },
        "examples": [
            {
                "input": {"destination": "Times Square"},
                "expected_output": {"action": "navigation", "data": {"destination": "Times Square"}}
            }
        ]
    },
    {
        "name": "control_device",
        "description": "Control device settings like Bluetooth, WiFi, Volume, Brightness, Airplane Mode",
        "parameters": ["setting", "action"],
        "parameter_schemas": {
            "setting": {
                "type": "string",
                "description": "Device setting (bluetooth, wifi, volume, brightness, airplane_mode)",
                "required": True,
                "enum": ["bluetooth", "wifi", "volume", "brightness", "airplane_mode"]
            },
            "action": {
                "type": "string",
                "description": "Action to perform (on, off, increase, decrease, toggle)",
                "required": True,
                "enum": ["on", "off", "increase", "decrease", "toggle"]
            },
            "value": {
                "type": "integer",
                "description": "Value for brightness/volume (0-100)",
                "required": False
            }
        },
        "examples": [
            {
                "input": {"setting": "bluetooth", "action": "on"},
                "expected_output": {"action": "device_control", "data": {"setting": "bluetooth", "action": "on"}}
            }
        ]
    },
    {
        "name": "open_app",
        "description": "Open an installed application by name",
        "parameters": ["app_name"],
        "parameter_schemas": {
            "app_name": {
                "type": "string",
                "description": "Name of the application to open (Gmail, Maps, Calendar, Chrome, YouTube, etc.)",
                "required": True
            }
        },
        "examples": [
            {
                "input": {"app_name": "Gmail"},
                "expected_output": {"action": "open_app", "data": {"app_name": "Gmail"}}
            }
        ]
    },
    {
        "name": "control_connectivity",
        "description": "Control WiFi or Bluetooth connectivity",
        "parameters": ["connectivity_type", "action"],
        "parameter_schemas": {
            "connectivity_type": {
                "type": "string",
                "description": "Type of connectivity (wifi, bluetooth)",
                "required": True,
                "enum": ["wifi", "bluetooth"]
            },
            "action": {
                "type": "string",
                "description": "Action (on, off, toggle)",
                "required": True,
                "enum": ["on", "off", "toggle"]
            }
        },
        "examples": [
            {
                "input": {"connectivity_type": "wifi", "action": "on"},
                "expected_output": {"action": "connectivity", "data": {"connectivity_type": "wifi", "action": "on"}}
            }
        ]
    }
]

# Export tool names for quick lookup
TOOL_NAMES = [tool["name"] for tool in TOOLS]

# Export tool descriptions
TOOL_DESCRIPTIONS = {tool["name"]: tool["description"] for tool in TOOLS}