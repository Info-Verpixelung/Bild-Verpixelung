# test_detect.py
import requests
import base64

with open("test.jpg", "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

payload = {
    "subject": "faces",
    "filename": "test.jpg",
    "type": "image/jpeg",
    "image": "data:image/jpeg;base64," + b64
}

r = requests.post(
    "http://127.0.0.1:5001/api/v1/detect",
    json=payload
)

print(r.json())
