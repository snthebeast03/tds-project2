from flask import Flask, request, jsonify
import os

app = Flask(__name__)

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
    
    return jsonify({"answer": full_input[:200]})  # Return preview of file content

# Make Flask work with Vercel (serverless)
from mangum import Mangum
handler = Mangum(app)
