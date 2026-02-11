from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import io
from PIL import Image

app = Flask(__name__)
CORS(app)

@app.route("/health", methods=["GET"])
def health():
    return "status ok"

def decode_data_url(data_url: str) -> Image.Image:
    # expected format: "data:image/jpeg;base64,...."
    if "," not in data_url:
        raise ValueError("Invalid data URL, missing comma separator")
    prefix, b64_data = data_url.split(",", 1)
    if not prefix.startswith("data:image/"):
        raise ValueError("Invalid data URL prefix")
    image_bytes = base64.b64decode(b64_data)
    return Image.open(io.BytesIO(image_bytes))

@app.route("/api/v1/detect", methods=["POST"])
def detect():
    """
    Expected JSON from frontend:
    {
      "subject": "faces" | "eyes" | "body",
      "image": "data:image/jpeg;base64,...",
      "filename": "photo001.jpg",
      "type": "image/jpeg"
    }
    """
    data = request.get_json(silent=True) or {}

    subject = data.get("subject")
    image_data_url = data.get("image")
    filename = data.get("filename")
    mime_type = data.get("type")

    # Basic validation
    if not subject or not image_data_url:
        return jsonify({
            "status": "error",
            "message": "Missing 'subject' or 'image' in request body",
            "objects": []
        }), 400

    try:
        # Decode image once; later you can pass this PIL image to your real detector
        img = decode_data_url(image_data_url)
        width, height = img.size
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to decode image: {e}",
            "objects": []
        }), 400

    # TODO: replace this stub with real detection
    # For now we just return a single box in the center so frontend can be tested
    dummy_box = {
        "type": "face",      # or use subject if you prefer
        "x": width // 2,     # center x
        "y": height // 2,    # center y
        "w": width // 3,     # box width
        "h": height // 3     # box height
    }

    return jsonify({
        "status": "success",
        "message": f"Dummy detection for {filename or 'image'} (subject={subject}, type={mime_type})",
        "objects": [dummy_box]
    })

if __name__ == "__main__":
    # Frontend uses http://localhost:5000/api/v1/detect
    app.run(host="0.0.0.0", port=5001, debug=True)
