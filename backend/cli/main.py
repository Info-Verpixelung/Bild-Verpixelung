# backend/cli/main.py
import argparse
import os
from engine.detector import detect
from engine.censor import censor
from engine.image_adapter import pil_to_np, np_to_pil
from PIL import Image

def process_image(file_path, mode="detect", censor_mode="pixelate", output_dir=None):
    image = Image.open(file_path).convert("RGB")
    np_img = pil_to_np(image)

    boxes = detect(np_img)

    if mode == "detect":
        print(f"Detected {len(boxes)} faces in {file_path}:")
        for box in boxes:
            print(box)
    elif mode == "censor":
        censored = censor(np_img, boxes, censor_mode)
        out_image = np_to_pil(censored)
        out_dir = output_dir or os.path.dirname(file_path)
        out_path = os.path.join(out_dir, f"censored_{os.path.basename(file_path)}")
        out_image.save(out_path)
        print(f"Censored image saved to {out_path}")
    else:
        raise ValueError("Invalid mode. Choose 'detect' or 'censor'.")

def main():
    parser = argparse.ArgumentParser(description="Face detection and censor CLI")
    parser.add_argument("input", help="Path to image file or folder")
    parser.add_argument("--mode", choices=["detect", "censor"], default="detect", help="Operation mode")
    parser.add_argument("--censor", choices=["pixelate", "blur"], default="pixelate", help="Censoring style")
    parser.add_argument("--output", help="Directory to save censored images (default: same as input)")

    args = parser.parse_args()
    input_path = args.input

    if os.path.isdir(input_path):
        # Process all images in directory
        for file_name in os.listdir(input_path):
            if file_name.lower().endswith((".png", ".jpg", ".jpeg")):
                process_image(os.path.join(input_path, file_name), args.mode, args.censor, args.output)
    else:
        process_image(input_path, args.mode, args.censor, args.output)

if __name__ == "__main__":
    main()
