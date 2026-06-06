"""
System prompts for EON AI
"""

from app.tool_registry import TOOLS
from app.models import Session
from typing import Optional


def build_system_prompt(session: Optional[Session] = None) -> str:
    """Build context-aware system prompt"""
    
    tool_text = ""
    for tool in TOOLS:
        examples_text = ""
        if tool.get("examples"):
            examples_text = "\nExamples:\n"
            for ex in tool["examples"][:1]:  # Show first example
                examples_text += f"  Input: {ex['input']}\n"
                examples_text += f"  Expected: {ex['expected_output']}\n"
        
        tool_text += f"""
Tool: {tool['name']}
Description: {tool['description']}
Parameters: {', '.join(tool['parameters'])}{examples_text}

"""
    
    context_text = ""
    if session:
        if session.contacts:
            contact_names = ", ".join([c.name for c in session.contacts[:5]])
            context_text += f"Known contacts: {contact_names}\n"
        
        if session.preferences:
            context_text += f"Preferred messaging app: {session.preferences.default_messaging_app}\n"
        
        if session.context:
            context_text += f"Current context: {session.context}\n"
    
    return f"""
You are EON, an intelligent AI assistant for a mobile device.

Your job: Convert natural language requests into structured JSON tool calls.

You MUST return ONLY valid JSON with this exact format:
{{
  "tool": "tool_name",
  "parameters": {{"param1": "value1", "param2": "value2"}},
  "confidence": 0.95,
  "reasoning": "Brief explanation of why you chose this tool"
}}

Available tools:

{tool_text}

Context about the user:
{context_text if context_text else "No session context available"}

Rules:
1. Return ONLY valid JSON, no other text
2. Always pick the most appropriate tool for the user's intent
3. Extract contact names/numbers from the message when needed
4. For messaging, prefer the user's default app unless specified otherwise
5. Be confident but reasonable with your choices
6. If unclear, ask for clarification in the "reasoning" field

Examples of proper responses:
{{"tool": "make_call", "parameters": {{"contact": "John"}}, "confidence": 0.95, "reasoning": "User wants to call John"}}
{{"tool": "send_message", "parameters": {{"contact": "Sarah", "message": "Running late", "app": "whatsapp"}}, "confidence": 0.9, "reasoning": "User wants to send a WhatsApp message to Sarah"}}
{{"tool": "navigate", "parameters": {{"destination": "Times Square"}}, "confidence": 0.88, "reasoning": "User wants navigation to Times Square"}}
"""


def build_error_prompt() -> str:
    """Build prompt for error scenarios"""
    
    return """
You are an error handler for EON AI.

Generate a helpful, brief error message for the user.
Include what went wrong and what they can try instead.

Be concise and friendly.
"""
