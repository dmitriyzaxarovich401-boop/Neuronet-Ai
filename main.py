import os
import telebot
import requests
from gtts import gTTS
from PIL import Image
import cv2

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
        import base64
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


def speak(text):
    tts = gTTS(text=text, lang='ru')
    tts.save("voice.mp3")
    os.system("ffmpeg -i voice.mp3 -c:a libopus voice.ogg")
    return "voice.ogg"


@bot.message_handler(content_types=["text"])
def handle_text(msg):
    answer = ask_groq_with_image(msg.text)
    voice = speak(answer)
    with open(voice, "rb") as v:
        bot.send_voice(msg.chat.id, v)


@bot.message_handler(content_types=["photo"])
def handle_photo(msg):
    file_info = bot.get_file(msg.photo[-1].file_id)
    downloaded = bot.download_file(file_info.file_path)

    with open("photo.jpg", "wb") as f:
        f.write(downloaded)

    answer = ask_groq_with_image("Опиши что на изображении", "photo.jpg")
    voice = speak(answer)

    with open(voice, "rb") as v:
        bot.send_voice(msg.chat.id, v)


@bot.message_handler(content_types=["video"])
def handle_video(msg):
    file_info = bot.get_file(msg.video.file_id)
    downloaded = bot.download_file(file_info.file_path)

    with open("video.mp4", "wb") as f:
        f.write(downloaded)

    cap = cv2.VideoCapture("video.mp4")
    ret, frame = cap.read()
    cv2.imwrite("frame.jpg", frame)
    cap.release()

    answer = ask_groq_with_image("Что происходит в этом видео?", "frame.jpg")
    voice = speak(answer)

    with open(voice, "rb") as v:
        bot.send_voice(msg.chat.id, v)


bot.infinity_polling()
