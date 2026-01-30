# Backend API Dokumentation

> für das backend-team: das hier ist alles was ihr vom frontend erwartet. damit ihr wisst mit was für requests ihr rechnen müsst und wie ihr damit arbeiten könnt.

---

## aktueller api-stand (jan 2026)

das frontend sendet derzeit nur einen endpoint an, aber dieser is eigentlich für die ganze detection-pipeline zuständig.

---

## endpoints

### `POST /api/v1/detect`

das frontend schickt hier einzelne bilder (als base64) zum backend, damit das backend die gewünschten merkmale erkennt und die koordinaten zurück gibt.

**wichtig zu wissen:**
- das frontend schickt ein bild pro request (nicht mehrere auf einmal)
- es wartet auf die response, bevor es das nächste bild schickt (sequentiell)
- wenn der user 5 bilder hochlädt, bekommt ihr 5 post-requests hintereinander

---

## request format

```json
{
  "subject": "faces",
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEA...",
  "filename": "photo_001.jpg",
  "type": "image/jpeg"
}
```

### was sind die felder:

| feld | typ | beispiel | beschreibung |
|------|-----|---------|-------------|
| `subject` | string | `"faces"` / `"eyes"` / `"body"` | was soll erkannt werden? der user wählt das aus nem dropdown |
| `image` | string | `"data:image/jpeg;base64,..."` | das komplette bild als base64 dataurl (nicht nur base64!) |
| `filename` | string | `"urlaub_2025.jpg"` | originaler dateiname (für logging und so) |
| `type` | string | `"image/jpeg"` / `"image/png"` | mime-type des bildes (auch fürs logging) |

---

## response format

das backend muss diese json zurück schicken:

```json
{
  "status": "success",
  "message": "<optional>",
  "objects": [
    {
      "type": "face",
      "x": 640,
      "y": 480,
      "w": 426,
      "h": 320
    },
    {
      "type": "face",
      "x": 200,
      "y": 150,
      "w": 300,
      "h": 280
    }
  ]
}
```

### response-felder erklärt:

| feld | typ | beschreibung |
|------|-----|-------------|
| `status` | string | `"success"` wenn alles geklappt hat, `"error"` bei problemen |
| `message` | string | kurze beschreibung was passiert is (wird im frontend geloggt) |
| `objects` | array | liste aller erkannten bereiche im bild |

### objekt-format (in `objects`):

| feld | typ | beschreibung |
|------|-----|-------------|
| `type` | string | der typ was erkannt wurde (z.b. `"face"`, `"eye"`, `"body"`) |
| `x` | integer | **mittelpunkt x-koordinate** des erkannten bereichs (nicht links-oben!) |
| `y` | integer | **mittelpunkt y-koordinate** des erkannten bereichs |
| `w` | integer | **breite** der bounding-box um den erkannten bereich |
| `h` | integer | **höhe** der bounding-box um den erkannten bereich |

wichtig: die x, y koordinaten sind der mittelpunkt der box, nicht die linke obere ecke! das frontend berechnet die ecken selbst.

---

## das base64 image problem

das bild kommt als dataurl an, nicht als reines base64. das sieht so aus:

```
data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/...
```

der teil `data:image/jpeg;base64,` is einfach nur nen prefix, das muss weg bevor ihr damit was anfangen könnt.

### python: base64 decodieren

```python
import base64
from PIL import Image
import io

# das kommt vom frontend
data_url = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEA..."

# 1. das "data:image/jpeg;base64," prefix entfernen
base64_string = data_url.split(",")[1]

# 2. base64 zu bytes decodieren
image_bytes = base64.b64decode(base64_string)

# 3. mit pillow nen image-objekt erstellen
image = Image.open(io.BytesIO(image_bytes))

# jetzt könnt ihr mit dem image arbeiten:
width, height = image.size
print(f"Bildgröße: {width}x{height}")

# oder direkt in numpy konvertieren (z.b. für opencv)
import numpy as np
image_array = np.array(image)
```

welche libraries braucht ihr?
- `pillow` (pil) - für einfache bildverarbeitung, größe auslesen, etc.
- `numpy` - wenn ihr mit arrays arbeiten wollt
- `opencv-python` - falls ihr ai-modelle wie face detection verwenden wollt
- `base64` - das is builtin in python, zum decodieren

installation:
```bash
pip install Pillow numpy opencv-python
```

---

## request-response ablauf (visuell)

```
frontend                          backend
   |                                |
   |------ post /api/v1/detect ------>
   |  (bild 1 als base64)           |
   |                                |  decodieren
   |                                |  erkennung laufen lassen...
   |                                |  (2-4 sekunden im test-setup)
   |<----- json mit objects --------|
   |  (koordinaten)                 |
   |                                |
   |------ post /api/v1/detect ------>
   |  (bild 2 als base64)           |
   |                                |  decodieren
   |                                |  erkennung...
   |<----- json mit objects --------|
   |                                |
   |  (usw. für alle bilder...)    |
```

das frontend wartet nach jedem request auf die response, bevor es das nächste bild schickt. ihr braucht euch also nicht darum kümmern, dass mehrere requests gleichzeitig kommen.

---

## praktische tipps

### debugging: was kommt an?

loggt einfach den request:

```python
@app.route('/api/v1/detect', methods=['POST'])
def detect_features():
    data = request.get_json()
    print(f"Subject: {data.get('subject')}")
    print(f"Filename: {data.get('filename')}")
    print(f"Image-Länge: {len(data.get('image', ''))} characters")
    # ...
```

### error handling

wenn was schiefgeht (z.b. ungültiges bild):

```python
try:
    base64_string = data_url.split(",")[1]
    image_bytes = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_bytes))
except Exception as e:
    return jsonify({
        "status": "error",
        "message": f"Bild konnte nicht dekodiert werden: {str(e)}"
    }), 400
```

das frontend zeigt dann dem user ne error-meldung und wartet auf feedback.

### response sollte bestmöglich schnell sein!

das frontend wartet auf die response, bevor es das nächste bild schickt. wenn die detection lange dauert (z.b. 10 sekunden), wartet der user entsprechend lange. der button sagt "⏳ Verarbeitung läuft..." also gib dem user visuelles feedback dass was passiert.

im test-setup verzögern wir die response um 2-4 sekunden absichtlich, damit sieht man die loading-balken-animation. bei echtem ml wird das natürlich länger dauern.

---

## was kommt als nächstes vom frontend?

aktuell (jan 2026) kann das frontend nur:
- bilder hochladen
- an `/api/v1/detect` schicken
- response empfangen und speichern

das frontend wird demnächst:
- die koordinaten aus der response nehmen
- rechtecke auf den bildern zeichnen (canvas api)
- preview mit markierungen zeigen

---

## beispiel: request mit echtem bild

das wäre ne echte base64 vom frontend (gekürzt, weil echte base64 mega lang sind):

```json
{
  "subject": "faces",
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAA4ADwDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8VAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA8A/9k",
  "filename": "selfie.jpg",
  "type": "image/jpeg"
}
```

die echte base64 wäre 10.000+ zeichen lang, deshalb hab ich das hier gekürzt.

---

stand: 30. jan 2026
format-version: 1.0
nächste docs-update: wenn das frontend canvas-rendering startet
