## Programm Starten (Frontend und Backend parallel) Stand 18.02.2026

### Einmalig:
- Miniconda installieren: https://www.anaconda.com/docs/getting-started/miniconda/main
- im Terminal "conda init" ausfuehren (je nach OS muss der command ggf. angepast werden, bei mac "conda init zsh")
- im Terminal in den backend Ordner navigieren, dann "conda env create -f environment-mac.yml" oder "conda env create -f environment-windows.yml" je nach OS

### Um das Programm auszuführen:
- Im Terminal in Bild-Verpixelung/backend navigieren
- "conda activate bildverpixelung" ausführen
- "python -m api.app" ausführen, das Programm sollte nun gestartet werden und das Frontend sollte sich automatisch im Browser öffnen.
