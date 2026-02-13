from flask import Flask
from flask_cors import CORS
from routes import detect_handler
import webbrowser
import threading
import time
import os
import subprocess  # Add this import

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
    """Startet npm dev server im frontend Ordner und öffnet Browser"""
    # Pfad zum frontend Ordner relativ zu app.py
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend"))

    if not os.path.exists(frontend_dir):
        print(f"Frontend-Ordner nicht gefunden: {frontend_dir}")
        return

    print("\nStarte Frontend automatisch...")
    print(f"Frontend-Ordner: {frontend_dir}")
    print()

    # 1. npm install (nur wenn node_modules fehlt oder --force)
    if not os.path.exists(os.path.join(frontend_dir, "node_modules")):
        print("Installiere npm Dependencies...")
        subprocess.Popen(["npm", "install"], cwd=frontend_dir)
        time.sleep(3)  # Kurze Pause für Installation
    else:
        print("node_modules bereits vorhanden")

    # 2. npm run dev starten (als separater Prozess)
    print("⚡ Starte Vite Dev Server (npm run dev)...")
    dev_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )

    # 4 Sekunden warten bis Vite-Server läuft
    print("Warte auf Vite Dev Server...")
    time.sleep(4)

    # 3. Browser öffnen (Vite läuft standardmäßig auf Port 5173)
    print("Öffne http://localhost:5173")
    webbrowser.open("http://localhost:5173")

if __name__ == "__main__":
    print("Bild-Verpixelungs-App startet...")
    print("Backend-Server auf http://localhost:5001")

    # Browser-Thread starten
    browser_thread = threading.Thread(target=open_frontend)
    browser_thread.daemon = True
    browser_thread.start()

    # Flask Server starten
    app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)
