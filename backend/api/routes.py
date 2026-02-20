from flask import request, jsonify
import base64
import io
from PIL import Image
import logging

# Logging einrichten (wird automatisch im Flask-Debug-Modus angezeigt)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def decode_data_url(data_url: str) -> Image.Image:
    """Konvertiert Data-URL zu PIL Image und loggt Details"""
    if "," not in data_url:
        raise ValueError("Invalid data URL: missing comma separator")

    prefix, b64_data = data_url.split(",", 1)

    # Log: Prefix prüfen
    logger.info(f"Data-URL Prefix: {prefix}")

    if not prefix.startswith("data:image/"):
        raise ValueError(f"Invalid data URL prefix: {prefix}")

    # Base64 decodieren
    image_bytes = base64.b64decode(b64_data)
    logger.info(f"Bildgröße (bytes): {len(image_bytes)}")

    # Zu PIL Image konvertieren
    image = Image.open(io.BytesIO(image_bytes))
    width, height = image.size

    logger.info(f"BILD EMPFANGEN: {request.json.get('filename', 'unknown')} | "
                f"Größe: {width}x{height} | "
                f"Subject: {request.json.get('subject', 'unknown')} | "
                f"MIME: {request.json.get('type', 'unknown')}")

    return image

def detect_objects_stub(image, subject: str, width: int, height: int):
    """Dummy Detection - später echte face_recognition hier rein"""

    # Einfache Dummy-Box in der Mitte des Bildes
    center_x = width // 2
    center_y = height // 2
    box_width = min(width, height) // 3
    box_height = box_width * 0.8  # etwas höher als breit

    logger.info(f"Dummy-Detection für '{subject}': Box bei x={center_x}, y={center_y}, w={box_width}, h={box_height}")

    return [{
        "type": subject if subject in ["face", "faces"] else "object",
        "x": center_x,
        "y": center_y,
        "w": box_width,
        "h": box_height
    }]

def detect_handler():
    """Haupt-Handler für /api/v1/detect"""

    # Request einlesen
    data = request.get_json(silent=True) or {}

    # Validierung
    required_fields = ["subject", "image", "filename", "type"]
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        logger.error(f"FEHLENDE FIELDS: {missing}")
        return jsonify({
            "status": "error",
            "message": f"Missing required fields: {', '.join(missing)}"
        }), 400

    subject = data["subject"]
    filename = data["filename"]
    image_data_url = data["image"]

    logger.info(f"Neuer Request: {filename} | Subject: {subject}")

    try:
        # 1. Bild decodieren
        image = decode_data_url(image_data_url)
        width, height = image.size

        # 2. Detection ausführen (aktuell Dummy)
        objects = detect_objects_stub(image, subject, width, height)

        # 3. Erfolgreiche Response
        response = {
            "status": "success",
            "message": f"Detection complete for {filename} ({len(objects)} objects found)",
            "objects": objects
        }

        logger.info(f"SUCCESS: {len(objects)} Objekte für {filename}")
        return jsonify(response)

    except Exception as e:
        logger.error(f"FEHLER bei {filename}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Processing failed: {str(e)}",
            "objects": []
        }), 500
