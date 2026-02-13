from flask import Flask
from flask_cors import CORS
from routes import detect_handler
import webbrowser
import threading
import time
import os

app = Flask(__name__)
CORS(app)

@app.route("/health", methods=["GET"])
def health():
    return "status ok"

@app.route("/api/v1/detect", methods=["POST"])
def detect():
    """Delegiert an die Engine in routes.py"""
    return detect_handler()

def open_frontend():
    """Öffnet direkt frontend/index.html im Browser"""
    # Pfad zur index.html relativ zum backend/app.py
    frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/index.html"))

    print("\nÖffne Frontend automatisch...")
    print(f"📄 Starte: file://{frontend_path}")
    print()

    # 1 Sekunde warten bis Flask läuft
    time.sleep(1)

    # Direkt index.html öffnen
    webbrowser.open(f"file://{frontend_path}")

if __name__ == "__main__":
    print("Bild-Verpixelungs-App startet...")
    print("Backend-Server auf http://localhost:5001")

    # Browser-Thread starten
    browser_thread = threading.Thread(target=open_frontend)
    browser_thread.daemon = True
    browser_thread.start()

    # Flask mit deinen gewünschten Settings
    app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)
