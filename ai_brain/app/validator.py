from app.tool_registry import TOOLS

def validate_tool_call(tool_call):

    if "tool" not in tool_call:
        return False, "Missing tool field"

    tool_name = tool_call["tool"]

    selected_tool = None

    for tool in TOOLS:
        if tool["name"] == tool_name:
            selected_tool = tool
            break

    if selected_tool is None:
        return False, f"Unknown tool: {tool_name}"

    if "parameters" not in tool_call:
        return False, "Missing parameters field"

    parameters = tool_call["parameters"]

    for required_param in selected_tool["parameters"]:

        if required_param not in parameters:
            return False, f"Missing parameter: {required_param}"

    return True, "Valid"