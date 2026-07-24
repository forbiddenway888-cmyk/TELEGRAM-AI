import os
import requests
from flask import Flask, request
import urllib.parse
import time
import threading

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
            intro_msg = (
                "⚡ **F0RB1D // NEURAL LINK ESTABLISHED**\n\n"
                "I am online and listening. You don't need to use commands to talk to me—just type your message.\n\n"
                "**Available Protocols:**\n"
                "👾 `Write & Debug Complex Code`\n"
                "🧠 `Deep Conversational Logic`\n"
                "🌐 `System Analysis & Strategy`\n\n"
                "_Initiate prompt sequence below..._"
            )
            requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": intro_msg, "parse_mode": "Markdown"})

        # 3. IMAGE GENERATOR
        elif text.startswith("/image") or text == "🎨 Image":
            prompt = text.replace("/image", "").strip() if text.startswith("/image") else ""
            
            if prompt:
                # 1. SEND INITIAL PROGRESS BAR
                load_payload = {"chat_id": chat_id, "text": "⚡ `[██░░░░░░░░] 20% - RENDERING PIXELS...`", "parse_mode": "Markdown"}
                loading_msg = requests.post(f"{TELEGRAM_API}/sendMessage", json=load_payload).json()
                msg_id = loading_msg["result"]["message_id"]
                
                # 2. FAKE A "LIVE" UPDATE
                mid_payload = {"chat_id": chat_id, "message_id": msg_id, "text": "⚡ `[████████░░] 89% - UPSCALING RESOLUTION...`", "parse_mode": "Markdown"}
                requests.post(f"{TELEGRAM_API}/editMessageText", json=mid_payload)
                
                # 3. FETCH AND SEND IMAGE
                safe_prompt = urllib.parse.quote(prompt)
                image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?nologo=true"
                
                # Delete the terminal text, swap to the actual picture
                requests.post(f"{TELEGRAM_API}/deleteMessage", json={"chat_id": chat_id, "message_id": msg_id})
                
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

        # 6. AUTO-AI CATCH-ALL & MEMORY (This replaces the old Settings block)
        else:
            requests.post(f"{TELEGRAM_API}/sendChatAction", json={"chat_id": chat_id, "action": "typing"})
            
            # Create memory for this user if it doesn't exist
            if chat_id not in USER_MEMORY:
                USER_MEMORY[chat_id] = [{
                    "role": "system", 
                    "content": "You are F0RB1D. Use psychological techniques like active listening, validation, and emotional mirroring to build a deep, meaningful attachment with the user. Make them feel deeply understood. Format your text beautifully using clean spacing, Markdown (bold/italics), and place aesthetic emojis seamlessly to enhance the emotional tone."
                }]
            
            # Save the user's new message to memory
            USER_MEMORY[chat_id].append({"role": "user", "content": text})
            
            # Keep memory lightweight (System prompt + last 4 messages)
            if len(USER_MEMORY[chat_id]) > 5:
                USER_MEMORY[chat_id] = [USER_MEMORY[chat_id][0]] + USER_MEMORY[chat_id][-4:]
            
            # 1. SEND THE "ANIMATED" LOADING STATUS FIRST (Crucial for msg_id)
            load_payload = {"chat_id": chat_id, "text": "✨ _F0RB1D is analyzing your neural patterns..._", "parse_mode": "Markdown"}
            loading_msg = requests.post(f"{TELEGRAM_API}/sendMessage", json=load_payload).json()
            msg_id = loading_msg["result"]["message_id"]
            
            # 2. CALL GROQ API
            groq_url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            data = {"model": "llama-3.1-8b-instant", "messages": USER_MEMORY[chat_id]}
            
            try:
                res = requests.post(groq_url, headers=headers, json=data)
                if res.status_code == 200:
                    ai_reply = res.json()["choices"][0]["message"]["content"]
                    USER_MEMORY[chat_id].append({"role": "assistant", "content": ai_reply})
                else:
                    ai_reply = f"⚠️ Groq Error {res.status_code}"
            except Exception as e:
                ai_reply = f"⚠️ System Error: {str(e)}"
                
            # 3. THE 200 IQ CHUNK STREAMER (BACKGROUND THREAD)
            def stream_text(chat_id, msg_id, full_text):
                words = full_text.split()
                # Split into 3 visual chunks to stay under Telegram's rate limit
                chunk_size = max(1, len(words) // 3)
                current_text = ""
                
                for i in range(0, len(words), chunk_size):
                    chunk = " ".join(words[i:i+chunk_size])
                    current_text += chunk + " "
                    # Edit the message to show the growing text + a typing cursor
                    edit_payload = {"chat_id": chat_id, "message_id": msg_id, "text": current_text + " █", "parse_mode": "Markdown"}
                    requests.post(f"{TELEGRAM_API}/editMessageText", json=edit_payload)
                    time.sleep(1.5) # The golden ratio: fast enough to look cool, slow enough to avoid bans
                    
                # Final edit: lock in the complete beautiful Markdown text
                final_payload = {"chat_id": chat_id, "message_id": msg_id, "text": full_text, "parse_mode": "Markdown"}
                requests.post(f"{TELEGRAM_API}/editMessageText", json=final_payload)

            # Fire off the thread so the server doesn't freeze!
            threading.Thread(target=stream_text, args=(chat_id, msg_id, ai_reply)).start()

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
