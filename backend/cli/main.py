# backend/cli/main.py - AUTO SUBJECT SELECTION
import argparse
import os
from typing import List, Dict, Tuple
from engine.detector import detect
from engine.censor import censor
from engine.image_adapter import piltonp, nptopil
from PIL import Image

def dicts_to_censor_tuples(boxes: List[Dict]) -> List[Tuple[int, int, int, int]]:
    """Convert detector dicts → censor tuples (x,y,half_w,half_h)"""
    return [(box['x'], box['y'], box['w']//2, box['h']//2) for box in boxes]

def group_eyes_into_pairs(eye_boxes: List[Tuple[int, int, int, int]]) -> List[List[Tuple[int, int, int, int]]]:
    """Group left/right eyes into pairs for eyeBar mode"""
    if len(eye_boxes) % 2 != 0:
        print(f"Warning: {len(eye_boxes)} eyes (odd number) - ignoring last eye")
        eye_boxes = eye_boxes[:-1]

    pairs = []
    for i in range(0, len(eye_boxes), 2):
        left_eye = min(eye_boxes[i:i+2], key=lambda b: b[0])
        right_eye = max(eye_boxes[i:i+2], key=lambda b: b[0])
        pairs.append([left_eye, right_eye])
    return pairs

def auto_select_subject(censor_mode: str) -> str:
    """Automatically choose optimal subject based on censor mode"""
    if censor_mode == "eyeBar":
        return "eyes"
    return "face"  # pixel/blur → faces

def process_image(filepath: str, mode: str, censor_mode: str, output_dir: str | None = None):
    # AUTO SELECT SUBJECT 🎯
    subject = auto_select_subject(censor_mode)
    #print(f"Auto-selected subject: {subject} for mode: {censor_mode}")

    image = Image.open(filepath).convert("RGB")
    np_img = piltonp(image)

    detections = detect(np_img, subject)

    if mode == "detect":
        print(f"Detected {len(detections)} {subject} in {filepath}:")
        for d in detections:
            print(d)
        return

    if mode == "censor":
        if censor_mode == "eyeBar":
            eye_tuples = dicts_to_censor_tuples(detections)
            eye_pairs = group_eyes_into_pairs(eye_tuples)
            censored = censor(np_img, eye_pairs, censor_mode)
        else:
            censor_boxes = dicts_to_censor_tuples(detections)
            censored = censor(np_img, censor_boxes, censor_mode)

        out_image = nptopil(censored)
        outdir = output_dir or os.path.dirname(filepath) or "."
        os.makedirs(outdir, exist_ok=True)
        outpath = os.path.join(outdir, f"censored_{censor_mode}_{os.path.basename(filepath)}")
        out_image.save(outpath)
        print(f"Censored image saved: {outpath}")

def main():
    parser = argparse.ArgumentParser(description="Smart Face/Eye detection & censor CLI")
    parser.add_argument("input", help="Image file or folder")
    parser.add_argument("--mode", choices=["detect", "censor"], default="detect")
    parser.add_argument("--censor", choices=["pixel", "blur", "eyeBar"], default="pixel")
    parser.add_argument("--output", help="Output directory")
    # --subject REMOVED - now automatic! 🎉

    args = parser.parse_args()

    input_path = args.input
    if os.path.isdir(input_path):
        for fn in os.listdir(input_path):
            if fn.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                process_image(os.path.join(input_path, fn), args.mode, args.censor, args.output)
    else:
        process_image(input_path, args.mode, args.censor, args.output)

if __name__ == "__main__":
    main()
