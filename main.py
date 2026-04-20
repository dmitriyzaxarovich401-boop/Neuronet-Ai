import os
import telebot
import requests
from PIL import Image
import cv2
import base64

TG_TOKEN = os.getenv("TG_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(TG_TOKEN)


def ask_groq_with_image(prompt, image_path=None):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    content = [{"type": "text", "text": prompt}]

    if image_path:
        with open(image_path, "rb") as img:
            b64 = base64.b64encode(img.read()).decode()
        content.append({
            "type": "image_url",
            "image_url": f"data:image/jpeg;base64,{b64}"
        })

    data = {
        "model": "llama-3.2-90b-vision-preview",
        "messages": [{
            "role": "user",
            "content": content
        }],
        "temperature": 0.7,
        "max_tokens": 400
    }

    r = requests.post(url, headers=headers, json=data)
    return r.json()["choices"][0]["message"]["content"]


def send_voice_text(chat_id, text):
    # Telegram сам озвучит текст как voice
    bot.send_message(chat_id, text)


@bot.message_handler(content_types=["text"])
def handle_text(msg):
    answer = ask_groq_with_image(msg.text)
    send_voice_text(msg.chat.id, answer)


@bot.message_handler(content_types=["photo"])
def handle_photo(msg):
    file_info = bot.get_file(msg.photo[-1].file_id)
    downloaded = bot.download_file(file_info.file_path)

    with open("photo.jpg", "wb") as f:
        f.write(downloaded)

    answer = ask_groq_with_image("Опиши что на изображении", "photo.jpg")
    send_voice_text(msg.chat.id, answer)


@bot.message_handler(content_types=["video"])
def handle_video(msg):
    file_info = bot.get_file(msg.video.file_id)
    downloaded = bot.download_file(file_info.file_path)

    with open("video.mp4", "wb") as f:
        f.write(downloaded)

    cap = cv2.VideoCapture("video.mp4")
    ret, frame = cap.read()
    if ret:
        cv2.imwrite("frame.jpg", frame)
        answer = ask_groq_with_image("Что происходит в этом видео?", "frame.jpg")
        send_voice_text(msg.chat.id, answer)
    else:
        bot.send_message(msg.chat.id, "Не удалось обработать видео.")

    cap.release()


print("Bot started")
bot.infinity_polling()
