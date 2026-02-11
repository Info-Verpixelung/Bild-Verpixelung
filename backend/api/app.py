from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from routes import detect_handler
import webbrowser
import threading
import time
import os

app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)

# Statische Frontend-Dateien servieren
@app.route("/")
def serve_frontend():
    return send_from_directory("../frontend", "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory("../frontend", path)

@app.route("/health", methods=["GET"])
def health():
    return "status ok"

@app.route("/api/v1/detect", methods=["POST"])
def detect():
    return detect_handler()

def open_browser():
    """Öffnet automatisch http://localhost:5001 im Browser"""
    frontend_url = "http://localhost:5001"

    print("\n🚀 Öffne Frontend automatisch...")
    print(f"📱 Starte: {frontend_url}")
    print()

    # 2 Sekunden warten bis Flask läuft
    time.sleep(2)

    # Einfache HTTP-URL - funktioniert immer auch in PyInstaller!
    webbrowser.open_new_tab(frontend_url)

if __name__ == "__main__":
    print("🎯 Bild-Verpixelungs-App startet...")
    print("📡 Backend + Frontend auf http://localhost:5001")

    # Browser-Thread starten
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()

    # Deine gewünschten Settings
    app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)
