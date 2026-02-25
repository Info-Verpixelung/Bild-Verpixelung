# backend/engine/detector.py

from typing import List, Dict
import numpy as np
import face_recognition


def _normalize_subject(subject: str) -> str:
    """
    Normalize the subject string.
    Currently we only support faces, but this allows extension later.
    """
    if not subject:
        return "face"

    s = subject.strip().lower()
    if s in ("face", "faces"):
        return "face"

    # For now, unsupported subjects: return "face" but you could also
    # choose to return [] or raise an error.
    return "face"


def detect(np_img: np.ndarray, subject: str = "face") -> List[Dict]:
    """
    Detect faces in the given image and return bounding boxes in the format:
    [{ "type": "face", "x": center_x, "y": center_y, "w": width, "h": height }, ...]
    Coordinates (x, y) are the CENTER of the box, as required by the API docs.
    """

    # Normalize and decide behavior based on subject
    normalized_subject = _normalize_subject(subject)

    # If later you support other subjects, branch here:
    # if normalized_subject == "logo": ...
    # For now, only faces.
    if normalized_subject != "face":
        # No detection for unsupported subjects
        return []

    # Ensure image has the right shape and type
    if np_img.ndim != 3 or np_img.shape[2] != 3:
        raise ValueError(f"Expected RGB image with shape (H, W, 3), got {np_img.shape}")

    if np_img.dtype != np.uint8:
        np_img = np_img.astype(np.uint8)

    # Run face_recognition to get face locations
    # face_locations is a list of (top, right, bottom, left) in pixel coordinates
    face_locations = face_recognition.face_locations(np_img, model="hog")

    boxes: List[Dict] = []

    for (top, right, bottom, left) in face_locations:
        w = right - left
        h = bottom - top

        # Center coordinates
        x_center = left + w / 2.0
        y_center = top + h / 2.0

        boxes.append(
            {
                "type": "face",                # or "faces" if you prefer, but keep it consistent
                "x": int(round(x_center)),
                "y": int(round(y_center)),
                "w": int(round(w)),
                "h": int(round(h)),
            }
        )

    return boxes
