"""
Data models for the face censoring API.
Used for validation, documentation, and type hints.
"""

from typing import List, Dict, Any
from enum import Enum
import numpy as np
from PIL import Image


# === REQUEST SCHEMAS (from Frontend → API) ===
class SubjectType(str, Enum):
    """What the user wants to detect."""
    FACE = "face"      # Full faces (uses face_locations)
    EYES = "eyes"      # Eye regions only (uses landmarks)


class DetectionRequest(Dict[str, Any]):
    """POST /api/v1/detect request body."""
    subject: str              # "face" or "eyes"
    image: str                # Base64 data URL: "data:image/jpeg;base64,..."
    filename: str             # Original filename: "photo.jpg"
    type: str                 # MIME: "image/jpeg", "image/png"


# === CORE ENGINE DATA TYPES ===
class DetectionBox(Dict[str, Any]):
    """Single detection result - EXACT format expected by frontend."""
    type: str                 # "face" or "eye"
    x: int                    # CENTER x-coordinate (not top-left!)
    y: int                    # CENTER y-coordinate
    w: int                    # Width of bounding box
    h: int                    # Height of bounding box


class DetectionResult(Dict[str, Any]):
    """Response from detector.py → API → frontend."""
    status: str               # "success" or "error"
    message: str              # Human-readable status
    objects: List[DetectionBox]  # List of detected regions


# === CENSORING ENGINE INPUT/OUTPUT ===
class CensorMode(str, Enum):
    """Censoring styles the frontend will select later."""
    PIXELATE = "pixelate"    # Downsample + upsample (mosaic effect)
    BLACK_BAR = "black_bar"  # Solid black rectangle
    BLUR = "blur"            # Gaussian blur


def censor_input_schema():
    """What censor.py should expect."""
    return {
        "image": np.ndarray,           # HxWx3 RGB uint8 (from piltonp())
        "boxes": List[DetectionBox],   # List from detector.detect()
        "mode": CensorMode,            # How to censor each box
    }


def censor_output_schema():
    """What censor.py must return."""
    return np.ndarray  # HxWx3 RGB uint8 (input shape, censored regions applied)


# === USAGE EXAMPLES ===
if __name__ == "__main__":
    # Example detection result (what your detector returns now)
    example_box = DetectionBox(
        type="eye",
        x=640,
        y=480,
        w=80,
        h=40
    )

    example_detections = DetectionResult(
        status="success",
        message="2 eyes detected",
        objects=[example_box]
    )

    # Example censor input
    print("Censor input:", censor_input_schema())
    print("Expected censor output: numpy array (HxWx3, uint8)")
