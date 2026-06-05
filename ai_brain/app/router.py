# ai_brain/app/router.py
def route_tool(tool_call):

    tool = tool_call["tool"]

    if tool == "make_call":
        return {
            "action": "call",
            "data": tool_call["parameters"]
        }

    if tool == "send_message":
        return {
            "action": "message",
            "data": tool_call["parameters"]
        }

    if tool == "navigate":
        return {
            "action": "navigation",
            "data": tool_call["parameters"]
        }

    if tool == "control_device":
        return {
            "action": "device_control",
            "data": tool_call["parameters"]
        }

    return {
        "action": "unknown",
        "data": {}
    }