from flask import Blueprint, request, jsonify, send_file
from engine.detector import detect
from engine.censor import censor
from engine.image_adapter import pil_to_np, np_to_pil
from PIL import Image
import io

api = Blueprint("api", __name__)

@api.route("/detect", methods=["POST"])
def detect_faces():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file provided"}), 400

    image = Image.open(file).convert("RGB")
    boxes = detect(pil_to_np(image))

    return jsonify({
        "objects": [box.__dict__ for box in boxes]
    })


@api.route("/censor", methods=["POST"])
def censor_faces():
    file = request.files.get("file")
    mode = request.form.get("mode", "pixelate")

    image = Image.open(file).convert("RGB")
    np_img = pil_to_np(image)

    boxes = detect(np_img)
    result = censor(np_img, boxes, mode)

    out = io.BytesIO()
    np_to_pil(result).save(out, format="PNG")
    out.seek(0)

    return send_file(out, mimetype="image/png")
