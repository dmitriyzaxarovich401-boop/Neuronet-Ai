import os
import telebot
import requests

print("Starting bot...")

TG_TOKEN = os.getenv("TG_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TG_TOKEN:
    raise RuntimeError("TG_TOKEN missing")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY missing")

bot = telebot.TeleBot(TG_TOKEN)


def ask_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8,
        "max_tokens": 300
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]


@bot.message_handler(content_types=["text"])
def send_message(message):
    try:
        answer = ask_groq(message.text)
        bot.send_message(message.chat.id, answer)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")


print("Bot started successfully")
bot.infinity_polling()
