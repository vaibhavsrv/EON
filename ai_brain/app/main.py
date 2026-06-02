from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

from app.prompts import build_system_prompt
from app.validator import validate_tool_call

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
                "content": build_system_prompt()
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

    total_call = json.loads(output)

    is_valid, message = validate_tool_call(total_call)

    if not is_valid:
        return{
            "error": message
        }

    return total_call