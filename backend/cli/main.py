import argparse
import os
from typing import List, Dict, Tuple
from engine.detector import detect
from engine.censor import censor
from engine.image_adapter import piltonp, nptopil  # Fixed import names from your actual file
from PIL import Image

def dicts_to_censor_tuples(boxes: List[Dict]) -> List[Tuple[int, int, int, int]]:
    """Convert detector dicts → censor tuples (x,y,half_w,half_h)"""
    result = []
    for box in boxes:
        x, y, w, h = box['x'], box['y'], box['w'], box['h']
        result.append((x, y, w//2, h//2))  # ← THIS is what censor() expects
    return result

def process_image(filepath: str, mode: str, censor_mode: str = "pixel", output_dir: str | None = None, subject: str = "face"):
    image = Image.open(filepath).convert("RGB")
    np_img = piltonp(image)

    detections = detect(np_img, subject)  # List of dicts

    if mode == "detect":
        print(f"Detected {len(detections)} objects in {filepath}")
        for d in detections: print(d)
        return

    if mode == "censor":
        censor_boxes = dicts_to_censor_tuples(detections)  # ← THE FIX
        censored = censor(np_img, censor_boxes, censor_mode)
        out_image = nptopil(censored)
        outdir = output_dir or os.path.dirname(filepath) or "."
        os.makedirs(outdir, exist_ok=True)
        outpath = os.path.join(outdir, f"censored_{os.path.basename(filepath)}")
        out_image.save(outpath)
        print(f"Censored image saved to {outpath}")

def main():
    parser = argparse.ArgumentParser(description="Face detection & censor CLI")
    parser.add_argument("input", help="Image file or folder")
    parser.add_argument("--mode", choices=["detect", "censor"], default="detect")
    parser.add_argument("--censor", choices=["pixel"], default="pixel")  # Your censor only does 'pixel'
    parser.add_argument("--output", help="Output directory")
    parser.add_argument("--subject", choices=["face", "eyes"], default="face")
    args = parser.parse_args()

    input_path = args.input
    if os.path.isdir(input_path):
        for fn in os.listdir(input_path):
            if fn.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                process_image(os.path.join(input_path, fn), args.mode, args.censor, args.output, args.subject)
    else:
        process_image(input_path, args.mode, args.censor, args.output, args.subject)

if __name__ == "__main__":
    main()
