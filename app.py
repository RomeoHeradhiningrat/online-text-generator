import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, MessageHandler, Filters

app = Flask(__name__)

# Ambil token dari environment variable
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)

# Variabel global untuk menyimpan teks terbaru
latest_text = "Belum ada pesan masuk."

@app.route('/')
def index():
    return f"<h1>Pesan Terbaru:</h1><p>{latest_text}</p>"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    global latest_text
    update = Update.de_json(request.get_json(force=True), bot)

    if update.message and update.message.text:
        latest_text = update.message.text

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
