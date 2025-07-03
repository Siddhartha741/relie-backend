from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)

# ✅ Make sure /chat allows cross-origin POST requests
CORS(app, resources={r"/chat": {"origins": "*"}}, supports_credentials=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-8b-8192"

TRIGGER_WORDS = ["suicide", "self-harm", "kill myself", "hurt me"]
session_memory = {}

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_id = data.get("user_id")
    user_input = data.get("message")

    if any(trigger in user_input.lower() for trigger in TRIGGER_WORDS):
        return jsonify({"response": "I'm sensing something serious. Please talk to a professional or call a helpline."})

    if user_id not in session_memory:
        session_memory[user_id] = []

    if len(session_memory[user_id]) >= 10:
        return jsonify({"response": "That’s all for now. I’m here if you need to talk again later."})

    session_memory[user_id].append({"role": "user", "content": user_input})

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are Relie, an empathetic mental health chatbot. Respond with care and support."},
            *session_memory[user_id]
        ]
    }

    try:
        res = requests.post(GROQ_API_URL, headers=headers, json=payload)
        res.raise_for_status()
        bot_reply = res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("Groq error:", e)
        bot_reply = "⚠️ I couldn't connect to the support assistant right now. Please try again later."

    session_memory[user_id].append({"role": "assistant", "content": bot_reply})
    return jsonify({"response": bot_reply})

if __name__ == '__main__':
    app.run(debug=True)
