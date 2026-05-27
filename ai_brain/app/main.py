from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

import os
import json

load_dotenv(dotenv_path=".env")

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

app = FastAPI()

class Request(BaseModel):
    message: str

SYSTEM_PROMPT = """
You are EON.

You are an AI assistant that converts user requests into structured JSON tool calls.

Return ONLY valid JSON.

Available tools:

1. control_device
Parameters:
- setting
- action

2. navigate
Parameters:
- destination

3. send_message
Parameters:
- contact
- message

4. make_call
Parameters:
- contact

Examples:

User:
Turn bluetooth on

Output:
{
  "tool": "control_device",
  "input": {
    "setting": "bluetooth",
    "action": "on"
  }
}

User:
Call John

Output:
{
  "tool": "make_call",
  "input": {
    "contact": "John"
  }
}
"""

@app.get("/")
async def root():

    return {
        "status": "EON Brain Running"
    }

@app.post("/chat")
async def chat(req: Request):

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },

            {
                "role": "user",
                "content": req.message
            }
        ]
    )

    output = response.choices[0].message.content

    output = output.replace("```json", "")
    output = output.replace("```", "")

    return json.loads(output)