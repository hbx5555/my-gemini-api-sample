import json
import os

import google.generativeai as genai
from flask import Flask, jsonify, request, send_file, send_from_directory

# Get API key from environment variable
API_KEY = os.getenv('GEMINI_API_KEY')
if not API_KEY:
    raise ValueError("Please set the GEMINI_API_KEY environment variable")

genai.configure(api_key=API_KEY)

app = Flask(__name__)


@app.route("/")
def index():
    return send_file('web/index.html')


@app.route("/api/generate", methods=["POST"])
def generate_api():
    if request.method == "POST":
        if API_KEY == 'TODO':
            return jsonify({ "error": '''
                To get started, get an API key at
                https://g.co/ai/idxGetGeminiKey and enter it in
                main.py
                '''.replace('\n', '') })
        try:
            req_body = request.get_json()
            content = req_body.get("contents")
            model = genai.GenerativeModel(model_name=req_body.get("model"))
            response = model.generate_content(content, stream=True)
            def stream():
                for chunk in response:
                    yield 'data: %s\n\n' % json.dumps({ "text": chunk.text })

            return stream(), {'Content-Type': 'text/event-stream'}

        except Exception as e:
            return jsonify({ "error": str(e) })


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('web', path)


if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
