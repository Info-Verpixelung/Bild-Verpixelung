## Programm Starten (Frontend und Backend parallel) Stand 18.02.2026


# Über die Kommandozeile

## Windows

### Einmalig:

#### Miniconda installieren:
- https://www.anaconda.com/docs/getting-started/miniconda/main
- Im Terminal in den backend ordner des Projekts navigieren
- "conda init" ausfühhren
- Terminal schließen und wieder öffnen, wieder in \backend navigieren
- Überprüfen, on miniconda erfolgreich installiert wurde: "conda --version"
- Falls eine Versionsnummber zurückgegeben wird, hat die Installation funktioniert

#### Environment installieren:
- Environment installieren: "conda env create -f environment-windows.yml"
- Installierung überprüfen: "conda env list" -> "bildverpixelung" sollte aufgelistet werden

### Um das Programm auszuführen
- Im Terminal in den backend ordner des Projekts navigieren
- Das conda environment aktivieren: "conda activate bildverpixelung" -> vor dem Dateipfdas sollte "(bildverpixelung)" stehen, also "(bildverpixelung) C:\Users\..."
- "python -m api.app"

## Mac / Linux

#### Miniconda installieren:
- https://www.anaconda.com/docs/getting-started/miniconda/main, oder falls brew installiert ist im Terminal "brew install --cask miniconda" ausführen (empfohlen)
- Im Terminal in den backend ordner des Projekts navigieren
- "conda init zsh" ausfühhren
- Terminal schließen und wieder öffnen, wieder in \backend navigieren
- Überprüfen, on miniconda erfolgreich installiert wurde: "conda --version"
- Falls eine Versionsnummber zurückgegeben wird, hat die Installation funktioniert

#### Environment installieren:
- Environment installieren: "conda env create -f environment-mac.yml"
- Installierung überprüfen: "conda env list" -> "bildverpixelung" sollte aufgelistet werden

### Um das Programm auszuführen
- Im Terminal in den backend ordner des Projekts navigieren
- Das conda environment aktivieren: "conda activate bildverpixelung" -> vor dem Dateipfdas sollte "(bildverpixelung)" stehen, also "(bildverpixelung) C:\Users\..."
- "python -m api.app"


# Über das Executable
- Executable für sein Betriebssystem runterladen
- Ggf. wird das Ausführen durch das Betriebssystem blockier und es muss erlaubt werden
  - Bei Mac: Ausführen, dann in den Einstellung zu "Privacy & Security" navigieren, runterscrollen und "Open anyway" clicken.
- Das Programm sollte ausgeführt werden, das Frontend sollte sich automatisch im Browser öffnen
