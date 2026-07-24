import os
import requests
from flask import Flask, request
import urllib.parse

app = Flask(__name__)

TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
USER_MEMORY = {}

@app.route("/", methods=["GET"])
def index():
    return "⚡ F0RB1D PROTOCOL ONLINE", 200

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()
    
    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"]["text"]

        # 6. AUTO-AI CATCH-ALL & MEMORY
        else:
            requests.post(f"{TELEGRAM_API}/sendChatAction", json={"chat_id": chat_id, "action": "typing"})
            
            # Create memory for this user if it doesn't exist
            if chat_id not in USER_MEMORY:
                # The System Prompt: This secretly tells the AI to use emojis naturally and emotionally
                USER_MEMORY[chat_id] = [
                    {"role": "system", "content": "You are a friendly, highly intelligent AI. Use emojis dynamically and naturally woven into your sentences to connect emotionally with the user. Do not just put them at the end of sentences."}
                ]
            
            # Save the user's new message to memory
            USER_MEMORY[chat_id].append({"role": "user", "content": text})
            
            # Keep memory lightweight (System prompt + last 4 messages) to save bandwidth/tokens
            if len(USER_MEMORY[chat_id]) > 5:
                USER_MEMORY[chat_id] = [USER_MEMORY[chat_id][0]] + USER_MEMORY[chat_id][-4:]
            
            # Call Groq API using the memory array
            groq_url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            data = {"model": "llama-3.1-8b-instant", "messages": USER_MEMORY[chat_id]}
            
            try:
                res = requests.post(groq_url, headers=headers, json=data)
                if res.status_code == 200:
                    ai_reply = res.json()["choices"][0]["message"]["content"]
                    # Save the AI's reply to memory so it remembers the context for next time
                    USER_MEMORY[chat_id].append({"role": "assistant", "content": ai_reply})
                else:
                    ai_reply = f"⚠️ Groq Error {res.status_code}"
            except Exception as e:
                ai_reply = f"⚠️ System Error: {str(e)}"
                
            requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": ai_reply})
                    
                requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": ai_reply})
                return "OK", 200
        # ----------------------

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

        # 2. TRIGGER THE AI PROMPT
        elif text.startswith("/ai") or text == "🤖 AI":
            payload = {
                "chat_id": chat_id,
                "text": "🤖 What do you want to ask the AI?",
                "reply_markup": {"force_reply": True} 
            }
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
