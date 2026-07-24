import os
import requests
from flask import Flask, request
import urllib.parse

app = Flask(__name__)

TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

# 1. Register command menu with Telegram
def setup_bot_commands():
    commands_payload = {
        "commands": [
            {"command": "start", "description": "⚡ Initialize FORB1D PROTOCOL"},
            {"command": "ai", "description": "🤖 Query FORB1D AI"},
            {"command": "image", "description": "🎨 Generate AI Image"},
            {"command": "ops", "description": "📡 System Status"}
        ]
    }
    requests.post(f"{TELEGRAM_API}/setMyCommands", json=commands_payload)

# Run menu setup once when server starts
setup_bot_commands()

@app.route("/", methods=["GET"])
def index():
    return "⚡ FORB1D PROTOCOL ONLINE", 200

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()
    
    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"]["text"]

        # START / HELP
        if text.startswith("/start"):
            payload = {
                "chat_id": chat_id,
                "text": "⚡ **FORB1D PROTOCOL ONLINE**\n\nUse the `/` key or menu button to browse commands."
            }
            requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

        # AI COMMAND (Simple Echo/Text Placeholder)
        elif text.startswith("/ai"):
            prompt = text.replace("/ai", "").strip()
            reply = f"🤖 **AI Response:** Processing prompt: *{prompt}*" if prompt else "Please provide a prompt after `/ai`."
            payload = {"chat_id": chat_id, "text": reply}
            requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

        # IMAGE GENERATOR (Zero Bandwidth)
        elif text.startswith("/image"):
            prompt = text.replace("/image", "").strip() or "cyberpunk city"
            safe_prompt = urllib.parse.quote(prompt)
            image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?nologo=true"
            payload = {
                "chat_id": chat_id,
                "photo": image_url,
                "caption": f"⚡ Generated: {prompt}"
            }
            requests.post(f"{TELEGRAM_API}/sendPhoto", json=payload)

        # SYSTEM OPS
        elif text.startswith("/ops"):
            payload = {"chat_id": chat_id, "text": "🟢 SYSTEM NOMINAL. Bandwidth usage: Ultra-Low."}
            requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
