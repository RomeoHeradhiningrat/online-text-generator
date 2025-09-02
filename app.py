from flask import Flask, request, jsonify
from flask_cors import CORS
import os, requests
from datetime import datetime, timezone

app = Flask(__name__)
CORS(app) # izinkan akses dari frontend mana pun (boleh dipersempit jika perlu)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "") # rahasiakan path webhook

STATE = {
    "text": "Belum ada pesan.",
    "updated_at": None,
    "from": None,
}

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def send_message(chat_id, text):
    """Kirim balasan ke Telegram (opsional)."""
    if not BOT_TOKEN or not chat_id:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=3)
    except Exception:
        pass

@app.get("/")
def home():
    return jsonify({
        "service": "telegram-text-bridge",
        "ok": True,
        "latest": STATE,
        "hint": "Use GET /latest to read current text; POST /webhook/<WEBHOOK_SECRET> for Telegram",
    })

@app.get("/latest")
def latest():
    return jsonify({
        "text": STATE["text"],
        "updated_at": STATE["updated_at"],
        "from": STATE["from"],
})

@app.post("/webhook/<path:secret>")
def webhook(secret):
    # Validasi secret path
    if WEBHOOK_SECRET and secret != WEBHOOK_SECRET:
        return jsonify({"ok": False, "error": "wrong secret"}), 403
    
    data = request.get_json(silent=True) or {}
    message = data.get("message") or data.get("edited_message") or {}
    
    # Ambil teks dari message atau caption (kalau kirim foto+caption)
    text = (message.get("text") or message.get("caption") or "").strip()
    
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    
    sender = message.get("from") or {}
    sender_name = " ".join(filter(None, [sender.get("first_name"), sender.get("last_name")])) or sender.get("username") or str(chat_id)
    
    
    if text:
        STATE["text"] = text
        STATE["updated_at"] = now_iso()
        STATE["from"] = sender_name
        
        # Konfirmasi ke pengirim (optional)
        send_message(chat_id, "✅ Pesan diterima. Web sudah diperbarui.")
    
    return jsonify({"ok": True})


@app.get("/health")
def health():
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
