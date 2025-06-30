from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import google.generativeai as genai
import PyPDF2
import io

# ✅ Corrected here
app = Flask(__name__)
CORS(app)

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    api_key = "AIzaSyD6OC05RRnAf3IeBZPAj3QgdGTdUUiHLpc"

genai.configure(api_key=api_key)

# Initialize model
model = genai.GenerativeModel('gemini-1.5-pro')
chat = model.start_chat(history=[])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat_endpoint():
    if request.method == 'OPTIONS':
        return '', 204
        
    user_prompt = request.json.get("prompt")
    if not user_prompt: 
        return jsonify({"error": "No prompt provided"}), 400
    
    try:
        response = chat.send_message(user_prompt)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/make-notes', methods=['POST', 'OPTIONS'])
def make_notes():
    if request.method == 'OPTIONS':
        return '', 204
        
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    try:
        content = ""
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension == '.pdf':
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
            for page in pdf_reader.pages:
                content += page.extract_text() + "\n"
        elif file_extension in ['.txt', '.doc', '.docx']:
            content = file.read().decode('utf-8')
        else:
            return jsonify({"error": "Unsupported file format. Please upload PDF or text files."}), 400
        
        prompt = f"""Please create concise and structured notes from the following text.
        
        Include:
        - Main points and key concepts
        - Important details and examples
        - Any significant conclusions
        
        Text to summarize:
        {content}"""
        
        response = model.generate_content(prompt)
        
        return jsonify({
            "notes": response.text,
            "filename": file.filename
        })
    except PyPDF2.PdfReadError:
        return jsonify({"error": "Invalid or corrupted PDF file"}), 400
    except UnicodeDecodeError:
        return jsonify({"error": "Please upload a valid text file"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/embed-text', methods=['POST', 'OPTIONS'])
def embed_text():
    if request.method == 'OPTIONS':
        return '', 204
    return jsonify({"message": "Text embedding feature is coming soon!"})

@app.route('/ask-me-anything', methods=['POST', 'OPTIONS'])
def ask_me_anything():
    if request.method == 'OPTIONS':
        return '', 204
    return jsonify({"message": "Ask Me Anything feature is coming soon!"})

# ✅ Corrected here as well
if __name__ == '__main__':
    app.run(debug=True)
