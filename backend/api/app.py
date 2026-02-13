from flask import Flask, render_template
from flask_cors import CORS
from routes import detect_handler
import webbrowser
import threading
import time
import os
import sys

# Handle PyInstaller temp folder
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(os.path.dirname(__file__))

template_folder = os.path.join(base_path, "templates")
static_folder = os.path.join(base_path, "static")

app = Flask(
    __name__,
    template_folder=template_folder,
    static_folder=static_folder
)

CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health", methods=["GET"])
def health():
    return "status ok"

@app.route("/api/v1/detect", methods=["POST"])
def detect():
    return detect_handler()

def open_browser():
    time.sleep(1)
    webbrowser.open("http://localhost:5001")

if __name__ == "__main__":
    print("Bild-Verpixelungs-App startet...")
    print("Backend-Server auf http://localhost:5001")

    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()

    app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)
