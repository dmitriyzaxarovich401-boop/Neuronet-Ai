import os
import telebot
from openai import OpenAI

# Берём ключи из переменных окружения
GROQ_API_KEY = os.getenv("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")
TG_TOKEN = os.getenv("8740783234:AAGv_ma7OIVd5gLUYKSxndYKPO4aiIspWgQ")

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

bot = telebot.TeleBot(TG_TOKEN)


@bot.message_handler(content_types=["text"])
def send_message(message):
    user_text = message.text

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": user_text}],
            max_tokens=300,
            temperature=0.8,
        )

        bot.send_message(
            message.chat.id,
            response.choices[0].message.content
        )

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")


print("Bot started...")
bot.infinity_polling()
