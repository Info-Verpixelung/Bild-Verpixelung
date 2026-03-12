# Startmechanismus der Web-App. Kommunikation Frontend- Backend. 
from flask import Flask, render_template
from flask_cors import CORS
from api.routes import detect_handler, censor_handler # Import der nötigen Methoden von Routes.py
import webbrowser
import threading
import time
import os
import sys

#Handling von PyInstaller temp folder (sicherstellen, dass Dateipfade funktionieren, egal ob das Programm compliiert ist oder nicht)
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

#Definiert, wo FLASK die nötigen Dateien findet, um die Webseite laufen zu lassen
template_folder = os.path.join(base_path, "templates")  # HTML- page
static_folder = os.path.join(base_path, "static")       # für Funktion der Website notwendiger Rest (Bilder, java script...)

#Initialisiert den Web Server
app = Flask(
    __name__,
    template_folder=template_folder,
    static_folder=static_folder
)

#Erlaubt Cross-Origin- Requests (Website, die auf einen anderen server zugreift)
CORS(app)

#Laden des html Dokumentes beim Öffnen der Seite
@app.route("/")
def index():
    return render_template("index.html")

#Test-Punkt
@app.route("/health", methods=["GET"])
def health():
    return "status ok"

# Kommunikation mit Backend für Gesichtserkennung und Zensierung. 
@app.route("/api/v1/detect", methods=["POST"])
def detect():                           # Definieren einer detect-Methode, die auf detect_handler von routes.py basiert
    return detect_handler()

@app.route("/api/v1/censor", methods=["POST"])
def censor():                           # Definieren einer censor-Methode, die auf censor_handler von routes.py basiert
    return censor_handler()

# Öffnet automatisch den Browser
def open_browser():
    time.sleep(1)                       # Nach kurzer Verzögerung
    webbrowser.open("http://localhost:5001")

# Öffnet den Server
if __name__ == "__main__":
    print("Bild-Verpixelungs-App startet...")
    print("Backend-Server auf http://localhost:5001")

    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()

    app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)
