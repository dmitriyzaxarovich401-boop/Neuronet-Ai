from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
import os

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class Question(BaseModel):
    message: str

# 👉 Страница с интерфейсом
@app.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 👉 API для чата
@app.post("/ask")
async def ask_ai(question: Question):
    completion = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {"role": "system", "content": "Ты полезный ИИ помощник."},
            {"role": "user", "content": question.message}
        ],
        temperature=0.7,
    )

    return {"answer": completion.choices[0].message.content}
