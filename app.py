from flask import Flask, request, jsonify
import requests
import os
import io
import zipfile
import fitz  # PyMuPDF
import pandas as pd

app = Flask(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def extract_text_from_pdf(file_stream):
    doc = fitz.open(stream=file_stream, filetype="pdf")
    return "\n".join([page.get_text() for page in doc])

def extract_text_from_excel(file_stream):
    try:
        excel_file = pd.read_excel(file_stream, sheet_name=None)
        text = ""
        for sheet_name, sheet in excel_file.items():
            text += f"\n\n--- Sheet: {sheet_name} ---\n"
            text += sheet.to_string(index=False)
        return text
    except Exception as e:
        return f"Failed to parse Excel: {e}"

def extract_text_from_zip(file_stream):
    extracted_text = ""
    with zipfile.ZipFile(file_stream) as z:
        for name in z.namelist():
            with z.open(name) as f:
                if name.endswith(".txt"):
                    extracted_text += f"\n\n--- {name} ---\n" + f.read().decode("utf-8", errors="ignore")
                elif name.endswith(".pdf"):
                    extracted_text += f"\n\n--- {name} (PDF) ---\n" + extract_text_from_pdf(f)
                elif name.endswith(".xlsx") or name.endswith(".xls"):
                    extracted_text += f"\n\n--- {name} (Excel) ---\n" + extract_text_from_excel(f)
    return extracted_text

@app.route('/api/', methods=['POST'])
def answer_question():
    question = request.form.get('question')
    file = request.files.get('file')  # Optional

    if not question:
        return jsonify({"error": "Missing question parameter"}), 400

    file_content = ""
    if file:
        filename = file.filename.lower()
        if filename.endswith('.pdf'):
            file_content = extract_text_from_pdf(file.stream)
        elif filename.endswith('.xlsx') or filename.endswith('.xls'):
            file_content = extract_text_from_excel(file)
        elif filename.endswith('.zip'):
            file_content = extract_text_from_zip(file)
        else:
            file_content = file.read().decode("utf-8", errors="ignore")

    full_input = f"{question}\n\n{file_content}"

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
