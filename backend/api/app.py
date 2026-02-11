from flask import Flask, request, jsonify
from flask_cors import CORS
from routes import detect_handler
import webbrowser
import threading
import time
import os

app = Flask(__name__)

# CORS für file:// (origin=null) + localhost + ALLES
CORS(app,
     resources={r"/*": {
         "origins": ["*"],
         "methods": ["GET", "POST", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"]
     }},
     supports_credentials=False)

@app.after_request
def after_request(response):
    """Manuelles CORS-Header-Setzen für file:// origin=null"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Max-Age', '86400')
    return response

@app.route("/health", methods=["GET"])
def health():
    return "status ok"

@app.route("/api/v1/detect", methods=["POST", "OPTIONS"])
def detect():
    if request.method == "OPTIONS":
        return "", 200

    print("🎯 POST /api/v1/detect ANGEKOMMEN!")  # DEBUG
    return detect_handler()

def open_frontend():
    frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/index.html"))
    print("\n🚀 Öffne Frontend...")
    print(f"📄 {frontend_path}")
    print("📡 Backend: http://localhost:5001")
    print("🔍 F12 → Console/Network prüfen!")

    time.sleep(1)
    webbrowser.open(f"file://{frontend_path}")

if __name__ == "__main__":
    print("🎯 Bild-Verpixelungs-App startet...")
    browser_thread = threading.Thread(target=open_frontend)
    browser_thread.daemon = True
    browser_thread.start()

    app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)
