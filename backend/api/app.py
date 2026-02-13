from flask import Flask
from flask_cors import CORS
from routes import detect_handler
import webbrowser
import threading
import time
import os
import subprocess
import sys
import shutil

app = Flask(__name__)
CORS(app)

@app.route("/health", methods=["GET"])
def health():
    return "status ok"

@app.route("/api/v1/detect", methods=["POST"])
def detect():
    """Delegiert an die Engine in routes.py"""
    return detect_handler()

def find_frontend_dir():
    """Findet frontend Ordner - funktioniert für dev und executable"""
    candidates = []

    # 1. Versuche relatives Pfad (Development)
    if hasattr(sys, '_MEIPASS'):  # PyInstaller executable
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(__file__)

    candidate1 = os.path.abspath(os.path.join(base_path, "../../frontend"))
    candidates.append(candidate1)

    # 2. Suche in Parent-Verzeichnissen (für verschiedene Packaging-Layouts)
    current = os.path.dirname(base_path)
    for i in range(5):  # Max 5 Ebenen hoch
        candidate = os.path.join(current, "frontend")
        if os.path.exists(candidate):
            candidates.append(os.path.abspath(candidate))
        current = os.path.dirname(current)

    # 3. Fallback: Suche im aktuellen Arbeitsverzeichnis
    candidates.append("./frontend")

    for candidate in candidates:
        if os.path.exists(candidate) and os.path.isdir(candidate):
            print(f"✅ Frontend gefunden: {candidate}")
            return candidate

    return None

def open_frontend():
    """Startet npm dev server im frontend Ordner - funktioniert für dev + executable"""
    frontend_dir = find_frontend_dir()

    if not frontend_dir:
        print("❌ Frontend-Ordner nicht gefunden!")
        print("Stelle sicher, dass der 'frontend' Ordner im gleichen Projekt wie app.py liegt.")
        print("Verfügbare Pfade gesucht:")
        candidates = []
        if hasattr(sys, '_MEIPASS'):
            candidates.append(os.path.dirname(sys.executable))
        else:
            candidates.append(os.path.dirname(__file__))
        candidates.append(os.getcwd())
        for path in candidates:
            print(f"  - {path}")
        return

    print(f"\n🚀 Starte Frontend automatisch...")
    print(f"Frontend-Ordner: {frontend_dir}")
    print()

    # 1. npm install (nur wenn node_modules fehlt)
    node_modules = os.path.join(frontend_dir, "node_modules")
    if not os.path.exists(node_modules):
        print("📦 Installiere npm Dependencies...")
        try:
            install = subprocess.Popen(
                ["npm", "install"],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            stdout, stderr = install.communicate(timeout=30)  # 30s Timeout
            if install.returncode != 0:
                print(f"⚠️  npm install Warnung: {stderr}")
            else:
                print("✅ npm install erfolgreich")
        except subprocess.TimeoutExpired:
            print("⚠️  npm install Timeout - fahre trotzdem fort...")
            install.kill()
    else:
        print("✅ node_modules bereits vorhanden")

    # 2. npm run dev starten (non-blocking)
    print("⚡ Starte Vite Dev Server (npm run dev)...")
    dev_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        start_new_session=True  # Wichtig für Executable: verhindert Termination
    )

    # 5 Sekunden warten bis Vite läuft
    print("⏳ Warte auf Vite Dev Server (Port 5173)...")
    time.sleep(5)

    # 3. Browser öffnen
    print("🌐 Öffne http://localhost:5173")
    webbrowser.open("http://localhost:5173")

    print("\n✅ Frontend läuft! Backend läuft auf http://localhost:5001")
    print("Beende mit Ctrl+C")

if __name__ == "__main__":
    print("Bild-Verpixelungs-App startet...")
    print("Backend-Server auf http://localhost:5001")

    # Browser-Thread starten
    browser_thread = threading.Thread(target=open_frontend)
    browser_thread.daemon = True
    browser_thread.start()

    # Flask Server starten
    app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)
