from flask import Flask, render_template
from flask_cors import CORS
from api.routes import detect_handler, censor_handler # import missing censor_handler
import webbrowser
import threading
import time
import os
import sys

# Handle PyInstaller temp folder (make sure paths work no matter if the programm is compiled or not)
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# defines where Flask finds the files neccessary to run the Website 
template_folder = os.path.join(base_path, "templates") # HTML- page
static_folder = os.path.join(base_path, "static") # Everything else (pictures, java script...)

# Initialising the Web Server
app = Flask(
    __name__,
    template_folder=template_folder,
    static_folder=static_folder
)

# Allows Cross-Origin- Requests (Website acessing another server, here: the API) 
CORS(app)

#Load the html document when someone opens the page
@app.route("/")
def index():
    return render_template("index.html")

#Test point
@app.route("/health", methods=["GET"])
def health():
    return "status ok"

# Definition of the two APIs (?): detect and censor. Uses the methods in routes.py (who use methods in censor + communication with the face detection engine)
@app.route("/api/v1/detect", methods=["POST"])
def detect():
    return detect_handler()

@app.route("/api/v1/censor", methods=["POST"])
def censor():
    return censor_handler()

# Automatically opens browser
def open_browser():
    time.sleep(1)
    webbrowser.open("http://localhost:5001")

# Opens server 
if __name__ == "__main__":
    print("Bild-Verpixelungs-App startet...")
    print("Backend-Server auf http://localhost:5001")

    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()

    app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)
