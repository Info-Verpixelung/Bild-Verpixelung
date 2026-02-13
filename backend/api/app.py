import os
import sys
import subprocess
import threading
import time
import webbrowser
from flask import Flask
from flask_cors import CORS
from routes import detect_handler

def find_frontend_dir():
    """Findet frontend/ egal wo app.py liegt - SUPER robust"""

    # 1. Suche im Arbeitsverzeichnis (wo executable liegt)
    cwd = os.getcwd()
    candidates = [
        os.path.join(cwd, "frontend"),
        os.path.join(cwd, "backend", "frontend"),  # Falls falsch gepackt
    ]

    # 2. Suche relativ zu app.py/backend/
    if not hasattr(sys, '_MEIPASS'):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        candidates.extend([
            os.path.join(script_dir, "../frontend"),  # Development
            os.path.join(script_dir, "../../frontend"),  # Falls tiefer
        ])

    # 3. Suche in allen Parent-Verzeichnissen
    current = cwd
    for _ in range(10):
        test_path = os.path.join(current, "frontend")
        candidates.append(test_path)
        current = os.path.dirname(current)

    for candidate in candidates:
        if os.path.exists(candidate) and os.path.isdir(candidate) and os.path.exists(os.path.join(candidate, "package.json")):
            print(f"✅ Frontend gefunden: {candidate}")
            return candidate

    print("❌ KEIN frontend/ Ordner gefunden!")
    print("Suche überall...")
    print("Verfügbare Ordner:")
    for root, dirs, files in os.walk("/tmp" if sys.platform == "darwin" else "."):
        if "frontend" in dirs:
            print(f"  -> {root}/frontend")
    return None

# Rest bleibt gleich...
def open_frontend():
    frontend_dir = find_frontend_dir()
    if not frontend_dir:
        print("❌ Starte ohne Frontend")
        return

    print(f"\n🚀 Frontend: {frontend_dir}")

    # npm install & dev (wie vorher)
    node_modules = os.path.join(frontend_dir, "node_modules")
    if not os.path.exists(node_modules):
        print("📦 npm install...")
        subprocess.Popen(["npm", "install"], cwd=frontend_dir)
        time.sleep(5)

    print("⚡ npm run dev...")
    subprocess.Popen(["npm", "run", "dev"], cwd=frontend_dir, start_new_session=True)
    time.sleep(4)
    webbrowser.open("http://localhost:5173")

# Flask App (unverändert)
app = Flask(__name__)
CORS(app)

@app.route("/health", methods=["GET"])
def health(): return "status ok"

@app.route("/api/v1/detect", methods=["POST"])
def detect(): return detect_handler()

if __name__ == "__main__":
    print("Bild-Verpixelungs-App startet...")
    threading.Thread(target=open_frontend, daemon=True).start()
    app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)
