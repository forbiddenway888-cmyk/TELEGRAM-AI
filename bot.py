import os
import requests
from flask import Flask, request
import urllib.parse

app = Flask(__name__)

TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

@app.route("/", methods=["GET"])
def index():
    return "⚡ F0RB1D PROTOCOL ONLINE", 200

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()
    
    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"]["text"]

        # 1. START COMMAND & KEYBOARD MENU
        if text.startswith("/start"):
            # The custom button layout
            keyboard_layout = {
                "keyboard": [
                    [{"text": "🤖 AI"}, {"text": "🎨 Image"}],
                    [{"text": "📡 Ops"}, {"text": "⚙️ Settings"}]
                ],
                "resize_keyboard": True
            }
            
            payload = {
                "chat_id": chat_id,
                "text": "⚡ **F0RB1D // PROTOCOL ONLINE**\n\nSelect a system protocol below or type a command:",
                "reply_markup": keyboard_layout,
                "parse_mode": "Markdown"
            }
            requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

        # 2. AI (Works for both button click AND /ai command)
        elif text.startswith("/ai") or text == "🤖 AI":
            prompt = text.replace("/ai", "").strip() if text.startswith("/ai") else ""
            
            if prompt:
                reply = f"🤖 **AI Response:** Processing prompt: *{prompt}*"
            else:
                reply = "To use the AI, type `/ai [your question]`"
                
            payload = {"chat_id": chat_id, "text": reply, "parse_mode": "Markdown"}
            requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

        # 3. IMAGE GENERATOR (Works for both button click AND /image command)
        elif text.startswith("/image") or text == "🎨 Image":
            prompt = text.replace("/image", "").strip() if text.startswith("/image") else ""
            
            if prompt:
                safe_prompt = urllib.parse.quote(prompt)
                image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?nologo=true"
                payload = {
                    "chat_id": chat_id,
                    "photo": image_url,
                    "caption": f"⚡ Generated: {prompt}"
                }
                requests.post(f"{TELEGRAM_API}/sendPhoto", json=payload)
            else:
                payload = {"chat_id": chat_id, "text": "To generate an image, type `/image [your idea]`"}
                requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

        # 4. SYSTEM OPS
        elif text.startswith("/ops") or text == "📡 Ops":
            payload = {"chat_id": chat_id, "text": "🟢 SYSTEM NOMINAL. Bandwidth usage: Ultra-Low."}
            requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

        # 5. SETTINGS
        elif text == "⚙️ Settings":
            payload = {"chat_id": chat_id, "text": "⚙️ Settings module is currently locked."}
            requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
