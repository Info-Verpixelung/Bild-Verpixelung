# Erkennung von Gesichtern/ Augen mithilfe der KI, enthält Funktion, die "Koordinaten" der erkannten Boxen ausgibt
# backend/engine/detector.py
from typing import List, Dict
import numpy as np
import face_recognition


def _normalize_subject(subject: str) -> str:
    """
    Normalisierung verschiedener Inputs des frontends, so das Informatioen einheitlich sind und Unstimmichkeiten
    nicht zu Fehlern führen. -> Standardmäßig "face"
    """
    if not subject:
        return "face"

    s = subject.strip().lower()
    if s in ("face", "faces"):
        return "face"
    if s in ("eye", "eyes"):
        return "eyes"
    return "face"  # fallback


    #Bild als Numpy Array erkennen und parameter zurückgeben.
def detect(np_img: np.ndarray, subject: str = "face") -> List[Dict]:
    """
    Merkmal erkennen und als Liste parameter zurückgeben, im Format:
    [{ "type": "face"/"eye", "x": center_x, "y": center_y, "w": width, "h": height }, ...]
    Es wird also der Mittelpunkt angegeben und von dem aus die höhe und breite der Box.
    """
    normalized_subject = _normalize_subject(subject) #Normalisierung zur EInheitlichkeit

    #Formate überprüfen
    if np_img.ndim != 3 or np_img.shape[2] != 3: #Sichergehen dass RGB angegeben wird und nicht Grayscale oder was anderes
        raise ValueError(f"Expected RGB image with shape (H, W, 3), got {np_img.shape}")
    if np_img.dtype != np.uint8: #Überprüfung des Datentyps (uint8), sonst konvertieren
        np_img = np_img.astype(np.uint8)

    #Aufruf der KI
    face_locations = face_recognition.face_locations(np_img, model="hog") #Position der Gesichter
    face_landmarks_list = face_recognition.face_landmarks(np_img) #Typ (Linkes Auge, Rechtes Auge, etc.)
    #Hierbei entsprechen die Indexe einander, also face_locations[i] und face_landmarks_list[i] gehören zu dem gleichen Gesicht

    #Output Container
    boxes: List[Dict] = []

    #Jedes erkanntes Gesicht verarbeiten
    for i, (top, right, bottom, left) in enumerate(face_locations):
        face_landmarks = face_landmarks_list[i]  #landmark für das entsprechende Gesicht

        if normalized_subject == "face": #Fall: Ganzes Gesicht -> Berechnen der Größe der Box (um in unserem Mittelpunkt-Orientierten Format zurückgeben zu können, statt anhand der Ecken)
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

        elif normalized_subject == "eyes": #Gleiches System, nur für Augen statt ganze Gesichter
            left_eye_points = np.array(face_landmarks['left_eye'])
            right_eye_points = np.array(face_landmarks['right_eye'])

            #Linkes Auge anhand der Landmarks
            left_eye_left = int(np.min(left_eye_points[:, 0]))
            left_eye_top = int(np.min(left_eye_points[:, 1]))
            left_eye_right = int(np.max(left_eye_points[:, 0]))
            left_eye_bottom = int(np.max(left_eye_points[:, 1]))

            #Rechtes Auge anhand der Landmarks
            right_eye_left = int(np.min(right_eye_points[:, 0]))
            right_eye_top = int(np.min(right_eye_points[:, 1]))
            right_eye_right = int(np.max(right_eye_points[:, 0]))
            right_eye_bottom = int(np.max(right_eye_points[:, 1]))

            #Zu Mittelpunk Format konvertieren x,y,w,h format (selbiges wie oben)

            #Linkes Auge
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

            #Rechtes Auge
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
