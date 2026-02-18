# Bild-Verpixelung

## Frontend starten (bessere Kompatibilität für alle Platformen)

> Wichtig: **Nicht** frontend starten durch öffnen von index.html als Datei im Browser

Folgendes ausführen:

```bash
cd frontend
npm install
npm run dev
```

---

Note: API Requests könnten vorerst **nicht/nicht korrekt** funktionieren ([CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS))

Note_v2: Wie ich sehe ist "**[flask_cors](https://pypi.org/project/flask-cors/)**" aktuell im Branch backend bereits in Verwendung, daher sollte im Normalfall alles funktionieren.


## Programm Starten (Frontend und Backend parallel) Stand 18.02.2026

>Einmalig:
- Miniconda installieren: https://www.anaconda.com/docs/getting-started/miniconda/main
- im Terminal "conda init" ausfuehren (je nach OS muss der command ggf. angepast werden, bei mac "conda init zsh")
- im Terminal in den backend Ordner navigieren, dann "conda env create -f backend/environment-mac.yml" oder "conda env create -f backend/environment-windows.yml" je nach OS

>Um das Programm auszuführen:
- Im Terminal in backend/api navigieren
- "conda activate bildverpixelung" ausführen
- "python backend/app.py" ausführen, das Programm sollte nun gestartet werden und das Frontend sollte sich automatisch im Browser öffnen.
