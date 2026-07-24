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

        # START COMMAND - Sends the Keyboard
        if text.startswith("/start"):
            # This builds the buttons exactly like your picture (2 on top, 2 on bottom)
            keyboard_layout = {
                "keyboard": [
                    [{"text": "🤖 AI"}, {"text": "🎨 Image"}],
                    [{"text": "📡 Ops"}, {"text": "⚙️ Settings"}]
                ],
                "resize_keyboard": True, # Makes it fit the screen perfectly
                "is_persistent": True    # Keeps the menu open at the bottom
            }
            
            payload = {
                "chat_id": chat_id,
                "text": "⚡ **F0RB1D // PROTOCOL ONLINE**\n\nSelect a system protocol below:",
                "reply_markup": keyboard_layout
            }
            requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

        # HANDLE BUTTON CLICKS
        elif text == "🤖 AI":
            payload = {"chat_id": chat_id, "text": "Send `/ai [your question]` to use the AI."}
            requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

        elif text == "🎨 Image":
            payload = {"chat_id": chat_id, "text": "Send `/image [prompt]` to generate a picture."}
            requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

        elif text == "📡 Ops":
            payload = {"chat_id": chat_id, "text": "🟢 SYSTEM NOMINAL. Bandwidth usage: Ultra-Low."}
            requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)
            
        elif text == "⚙️ Settings":
            payload = {"chat_id": chat_id, "text": "⚙️ Settings module is currently locked."}
            requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
