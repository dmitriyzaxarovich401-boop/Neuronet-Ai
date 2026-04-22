import os
import telebot
import requests
from flask import Flask, request

TG_TOKEN = os.getenv("TG_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(TG_TOKEN)
app = Flask(__name__)


def ask_groq(text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "llama-3.1-70b-versatile",
        "messages": [{"role": "user", "content": text}],
    }
    r = requests.post(url, headers=headers, json=data, timeout=60)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


@app.route(f"/{TG_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.data.decode("utf-8"))
    bot.process_new_updates([update])
    return "ok", 200


@bot.message_handler(content_types=["text"])
def handle_text(message):
    try:
        answer = ask_groq(message.text)
        bot.send_message(message.chat.id, answer)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")


@app.route("/")
def index():
    return "Bot is running"


if __name__ == "__main__":
    app.run()
