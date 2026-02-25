# backend/engine/detector.py
from typing import List, Dict
import numpy as np
import face_recognition


def _normalize_subject(subject: str) -> str:
    """
    Normalize the subject string.
    """
    if not subject:
        return "face"

    s = subject.strip().lower()
    if s in ("face", "faces"):
        return "face"
    if s in ("eye", "eyes"):
        return "eyes"
    return "face"  # fallback


def detect(np_img: np.ndarray, subject: str = "face") -> List[Dict]:
    """
    Detect faces/eyes and return bounding boxes in the format:
    [{ "type": "face"/"eye", "x": center_x, "y": center_y, "w": width, "h": height }, ...]
    """
    normalized_subject = _normalize_subject(subject)

    # Validate image (same as your original)
    if np_img.ndim != 3 or np_img.shape[2] != 3:
        raise ValueError(f"Expected RGB image with shape (H, W, 3), got {np_img.shape}")
    if np_img.dtype != np.uint8:
        np_img = np_img.astype(np.uint8)

    # Get BOTH face locations AND landmarks (landmarks includes face locations too)
    face_locations = face_recognition.face_locations(np_img, model="hog")
    face_landmarks_list = face_recognition.face_landmarks(np_img)

    boxes: List[Dict] = []

    # Process each detected face
    for i, (top, right, bottom, left) in enumerate(face_locations):
        face_landmarks = face_landmarks_list[i]  # corresponding landmarks for this face

        if normalized_subject == "face":
            # YOUR ORIGINAL WORKING FACE CODE - unchanged
            w = right - left
            h = bottom - top
            x_center = left + w / 2.0
            y_center = top + h / 2.0
            boxes.append({
                "type": "face",
                "x": int(round(x_center)),
                "y": int(round(y_center)),
                "w": int(round(w)),
                "h": int(round(h)),
            })

        elif normalized_subject == "eyes":
            # Precise eye landmarks
            left_eye_points = np.array(face_landmarks['left_eye'])
            right_eye_points = np.array(face_landmarks['right_eye'])

            # Left eye bounding box from actual landmark points
            left_eye_left = int(np.min(left_eye_points[:, 0]))
            left_eye_top = int(np.min(left_eye_points[:, 1]))
            left_eye_right = int(np.max(left_eye_points[:, 0]))
            left_eye_bottom = int(np.max(left_eye_points[:, 1]))

            # Right eye bounding box from actual landmark points
            right_eye_left = int(np.min(right_eye_points[:, 0]))
            right_eye_top = int(np.min(right_eye_points[:, 1]))
            right_eye_right = int(np.max(right_eye_points[:, 0]))
            right_eye_bottom = int(np.max(right_eye_points[:, 1]))

            # Convert to center x,y,w,h format (same as your face code)
            # Left eye
            left_w = left_eye_right - left_eye_left
            left_h = left_eye_bottom - left_eye_top
            left_x = left_eye_left + left_w / 2.0
            left_y = left_eye_top + left_h / 2.0
            boxes.append({
                "type": "eye",
                "x": int(round(left_x)),
                "y": int(round(left_y)),
                "w": int(round(left_w)),
                "h": int(round(left_h)),
            })

            # Right eye
            right_w = right_eye_right - right_eye_left
            right_h = right_eye_bottom - right_eye_top
            right_x = right_eye_left + right_w / 2.0
            right_y = right_eye_top + right_h / 2.0
            boxes.append({
                "type": "eye",
                "x": int(round(right_x)),
                "y": int(round(right_y)),
                "w": int(round(right_w)),
                "h": int(round(right_h)),
            })

    return boxes
