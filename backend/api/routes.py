# Handelt Kommunikation 
#Import von Bibliotheken
from flask import request, jsonify
import base64
import io
from PIL import Image
import logging

# Import von Modulen des eigenen Projektes
from engine.image_adapter import piltonp, nptopil
from engine.detector import detect
from engine.censor import censor
from api.schemas import CensorMode

# Logging einrichten (wird automatisch im Flask-Debug-Modus angezeigt)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#Konvertiert Data-URL zu PIL Image und loggt Details
def decode_data_url(data_url: str) -> Image.Image:
    # Trennt "Metadaten"/ Präfix des Bildes von Daten
    if "," not in data_url:
        raise ValueError("Invalid data URL: missing comma separator")
    prefix, b64_data = data_url.split(",", 1)

    # Log: Präfix prüfen
    logger.info(f"Data-URL Prefix: {prefix}")

    #Fehlermeldung wenn Datei kein Bild ist (also Präfix nicht mit data:image/ started)
    if not prefix.startswith("data:image/"):
        raise ValueError(f"Invalid data URL prefix: {prefix}")

    # Base64 decodieren (zu Bytes)
    image_bytes = base64.b64decode(b64_data)
    logger.info(f"Bildgröße (bytes): {len(image_bytes)}")

    # Bytes wieder zu PIL Image konvertieren, Größe speichern
    image = Image.open(io.BytesIO(image_bytes))
    width, height = image.size

    #Logging
    logger.info(f"BILD EMPFANGEN: {request.json.get('filename', 'unknown')} | "
                f"Größe: {width}x{height} | "
                f"Subject: {request.json.get('subject', 'unknown')} | "
                f"MIME: {request.json.get('type', 'unknown')}")

    return image

def detect_handler():
    """Haupt-Handler für /api/v1/detect"""

    data = request.get_json(silent=True) or {}               # Request einlesen

    # Validierung + Test ob alle benötigten Fields enthalten 
    required_fields = ["subject", "image", "filename", "type"]
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        logger.error(f"FEHLENDE FIELDS: {missing}")
        return jsonify({
            "status": "error",
            "message": f"Missing required fields: {', '.join(missing)}"
        }), 400                                             #Fehlermeldung, die "bad response" entspricht
    
    # Infos aus Request in Variablen speichern
    subject = data["subject"]
    filename = data["filename"]
    image_data_url = data["image"]

    logger.info(f"Neuer Request: {filename} | Subject: {subject}")

    try:
        # 1. Bild decodieren
        image = decode_data_url(image_data_url)             # PIL image erstellen
        np_img = piltonp(image)                             # in numpy array umwandeln 

        # 2. Detection/ Erkennung von Gesichtern bzw. Augen durchführen (nutzen der detect methode von engine.detector)
        objects = detect(np_img, subject)

        # 3. Erfolgreiche Response
        response = {
            "status": "success",
            "message": f"Detection complete for {filename}, {len(objects)} objects found",
            "objects": objects,
        }

        logger.info(f"SUCCESS: {len(objects)} Objekte für {filename}")  # Logging

        return jsonify(response)                                        #Return der response

    # Error handling aller anderen Fehler, wird in Response angegeben 
    except Exception as e:
        logger.error(f"FEHLER bei {filename}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Processing failed: {str(e)}",
            "objects": []
        }), 500                                                         # Fehlermeldung, die für "internal server error" steht

# Definiert wie die Anonymisierung angewendet wird 
def censor_handler():
    data = request.get_json()                   # Request einlesen
    required = ["image", "boxes", "mode"]       # Definieren, was in Request benötigt wird -> Fehlermeldung wenn nicht vorhanden
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"status": "error", "message": f"Missing: {', '.join(missing)}"}), 400

    try:
        pil_image = decode_data_url(data["image"])                      # Umwandlung der Bilddaten in Request in pil
        np_image = piltonp(pil_image)                                   # ... und dann zu numpy array
        censored_np = censor(np_image, data["boxes"], data["mode"])     # Aufruf der censor- Methode, speichern des anonymisierten Bildes
        censored_pil = nptopil(censored_np)                             # ... und Umwandlung in ein pil

        buffer = io.BytesIO()                                           
        censored_pil.save(buffer, format="PNG", optimize=True)          # Bild als PNG im RAM speichern
        img_str = base64.b64encode(buffer.getvalue()).decode()          # Bild wieder zu base64 umwandeln
        data_url = f"data:image/png;base64,{img_str}"                   # ... mit dem richtigen Präfix

        return jsonify({                                                # Response senden 
            "status": "success",
            "message": f"Censored {len(data['boxes'])} regions",
            "censored_image": data_url
        })
    
    except Exception as e:                                              #Error handling aller anderen Fehler 
        logger.error(f"Censor error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500     # Fehlermeldung, die für "internal server error" steht
