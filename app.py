from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

LLM_API_URL = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
AIPROXY_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZjEwMDE1OTlAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.uTR9VdsvciCVXRPPt17VxRA34LK1Xolxom_2QOVMpiA"  # Set on Render as env var

@app.route('/api/', methods=['POST'])
def answer_question():
    question = request.form.get('question')
    file = request.files.get('file')

    if not question:
        return jsonify({"error": "Missing question parameter"}), 400
    if not file:
        return jsonify({"error": "Missing file parameter"}), 400

    content = file.read().decode("utf-8", errors="ignore")
    full_input = f"{question}\n\n{content}"

    headers = {
        "Authorization": f"Bearer {AIPROXY_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": full_input}
        ]
    }

    try:
        response = requests.post(LLM_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        answer = data["choices"][0]["message"]["content"]
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
