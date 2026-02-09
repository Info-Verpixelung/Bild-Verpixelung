from flask import Blueprint, request, jsonify
import base64
import io
from PIL import Image

api = Blueprint("api", __name__)

@api.route("/api/v1/detect", methods=["POST"])
def detect():
    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "No JSON body received"
        }), 400

    try:
        # Logging (wichtig für Debug)
        print("📥 Detect request")
        print("Subject:", data.get("subject"))
        print("Filename:", data.get("filename"))

        # --- Base64 DataURL verarbeiten ---
        data_url = data["image"]
        base64_string = data_url.split(",")[1]
        image_bytes = base64.b64decode(base64_string)

        image = Image.open(io.BytesIO(image_bytes))
        width, height = image.size

        # --- TEMP: Dummy-Erkennung ---
        # Eine Box mittig im Bild
        objects = [{
            "type": data.get("subject", "face"),
            "x": width // 2,
            "y": height // 2,
            "w": width // 3,
            "h": height // 3
        }]

        return jsonify({
            "status": "success",
            "message": "Detection successful (dummy)",
            "objects": objects
        })

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({
            "status": "error",
            "message": f"Detection failed: {str(e)}"
        }), 400
