from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Set your proxy OpenAI-compatible endpoint
LLM_API_URL = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
LLM_API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZjEwMDE1OTlAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.uTR9VdsvciCVXRPPt17VxRA34LK1Xolxom_2QOVMpiA"  # Store in env vars or hardcode if needed

@app.route('/api/', methods=['POST'])
def answer_question():
    question = request.form.get('question')
    file = request.files.get('file')

    if not question:
        return jsonify({"error": "Missing question parameter"}), 400
    if not file:
        return jsonify({"error": "Missing file parameter"}), 400

    # Read uploaded file
    content = file.read().decode("utf-8", errors="ignore")
    full_input = f"{question}\n\n{content}"

    try:
        # Send to LLM proxy
        headers = {
            "Authorization": f"Bearer {LLM_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": full_input}
            ]
        }

        response = requests.post(LLM_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"]

        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
