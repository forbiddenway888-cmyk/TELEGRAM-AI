import os
import requests
from flask import Flask, request
import urllib.parse

app = Flask(__name__)

# Securely grab your token from Render Environment Variables
TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

# A simple keep-alive route for Uptime Robot
@app.route("/", methods=["GET"])
def index():
    return "⚡ FORB1D PROTOCOL IS ONLINE", 200

# The secret webhook route (using your token makes it unguessable)
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()
    
    # Catch messages
    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"]["text"]

        # 200 IQ IMAGE GENERATOR
        if text.startswith("/image"):
            # Grab what they typed after /image
            prompt = text.replace("/image", "").strip()
            
            if not prompt:
                prompt = "cyberpunk hacker terminal" # Default fallback
                
            # URL encode the prompt so it's safe for a web link
            safe_prompt = urllib.parse.quote(prompt)
            
            # The magical direct URL - Render never downloads this!
            image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?nologo=true"
            
            # Send the URL to Telegram. Telegram downloads it for us.
            payload = {
                "chat_id": chat_id,
                "photo": image_url,
                "caption": f"⚡ Generated: {prompt}\n[FORB1D PROTOCOL]"
            }
            requests.post(f"{TELEGRAM_API}/sendPhoto", json=payload)

        # Standard text response
        elif text.startswith("/ops"):
            payload = {
                "chat_id": chat_id,
                "text": "SYSTEM NOMINAL. Awaiting commands."
            }
            requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

    return "OK", 200

if __name__ == "__main__":
    # Render assigns a dynamic port, so we catch it here
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
