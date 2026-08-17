from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Store conversation history
conversation_history = []

# Chatbot personality
SYSTEM_PROMPT = """
You are StudyBuddy, a helpful and friendly AI assistant.

Your purpose is to help users learn programming,
technology, and academic topics.

Give clear and simple answers.
"""

# Context window management
MAX_HISTORY_MESSAGES = 10


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({
                "error": "Please enter a message."
            }), 400

        # Add user message to conversation history
        conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Keep only recent messages
        if len(conversation_history) > MAX_HISTORY_MESSAGES:
            conversation_history[:] = conversation_history[-MAX_HISTORY_MESSAGES:]

        # Add system prompt + conversation history
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ] + conversation_history

        # Send request to LLM
        response = client.responses.create(
            model="gpt-5.6",
            input=messages
        )

        assistant_message = response.output_text

        # Save bot response
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return jsonify({
            "reply": assistant_message
        })

    except Exception:
        return jsonify({
            "error": "Something went wrong while contacting the AI service."
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
