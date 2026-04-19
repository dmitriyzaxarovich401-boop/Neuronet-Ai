from fastapi import FastAPI
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("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"))

app = FastAPI()

class Question(BaseModel):
    message: str

@app.post("/ask")
async def ask_ai(question: Question):
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "Ты полезный ИИ помощник."},
            {"role": "user", "content": question.message}
        ],
        model="llama-3.1-70b-versatile",
        temperature=0.7,
    )

    return {"answer": chat_completion.choices[0].message.content}
