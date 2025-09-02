import os
from flask import Flask, render_template_string
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN belum di-set di Render!")

# variabel untuk menyimpan teks terakhir
latest_text = "Belum ada pesan"

# inisialisasi Flask
app = Flask(__name__)

# inisialisasi bot
application = Application.builder().token(TOKEN).build()

# handler pesan masuk
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global latest_text
    latest_text = update.message.text
    await update.message.reply_text(f"Teks '{latest_text}' sudah ditampilkan di web!")

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# halaman web
@app.route("/")
def home():
    return render_template_string("""
        <h1>Pesan Terakhir dari Telegram:</h1>
        <p style="font-size:20px; color:blue;">{{text}}</p>
    """, text=latest_text)

# jalanin flask + telegram bot
if __name__ == "__main__":
    import threading

    def run_bot():
        application.run_polling()

    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=5000)
