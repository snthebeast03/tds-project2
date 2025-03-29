from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = "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"  # Set in env

@app.route('/api/', methods=['POST'])
def answer_question():
    question = request.form.get('question')
    file = request.files.get('file')  # Optional

    if not question:
        return jsonify({"error": "Missing question parameter"}), 400

    # Combine question and file (if present)
    content = file.read().decode("utf-8", errors="ignore") if file else ""
    full_input = f"{question}\n\n{content}"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": full_input}
        ]
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        answer = data["choices"][0]["message"]["content"]
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
