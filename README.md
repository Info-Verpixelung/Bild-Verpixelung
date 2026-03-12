
# Bild-Verpixelung
---

Eine Anwendung zur automatischen Zensur / Anonymisierung von Gesichtern.

# Inhaltsverzeichnis

- [Bild-Verpixelung](#bild-verpixelung)
- [Zweck der Anwendung](#zweck-der-anwendung)
- [Verwendete Technologien](#verwendete-technologien)

- [Starten über die Kommandozeile](#starten-über-die-kommandozeile)
    - [Windows](#windows)
        - [Einmalige Einrichtung](#einmalige-einrichtung)
            - [Miniconda installieren](#miniconda-installieren)
            - [Environment erstellen](#environment-erstellen)
        - [Programm ausführen](#programm-ausführen)
    - [macOS / Linux](#macos--linux)
        - [Einmalige Einrichtung](#einmalige-einrichtung-1)
            - [Miniconda installieren](#miniconda-installieren-1)
            - [Environment erstellen](#environment-erstellen-1)
        - [Programm ausführen](#programm-ausführen-1)

- [Starten über das Executable](#starten-über-das-executable)

- [CLI-Anwendung — Bildanalyse & Zensur](#cli-anwendung--bildanalyse--zensur)
    - [CLI ausführen](#cli-ausführen)
    - [Command-Struktur](#command-struktur)
    - [Parameter im Detail](#parameter-im-detail)
        - [INPUT](#input)
    - [Mode-Parameter](#mode-parameter)
        - [detect](#detect)
        - [censor](#censor)
    - [Censor-Parameter](#censor-parameter)
    - [Automatische Objektauswahl](#automatische-objektauswahl)
    - [Output-Parameter](#output-parameter)
    - [Mehrere Bilder verarbeiten](#mehrere-bilder-verarbeiten)

---

# Zweck der Anwendung

Es kann verschiedene Gründe haben, warum man Gesichter in Fotos zensieren will, für diese wurde diese Anwendung konzipiert.
Vor allem für Bilder von Demonstrationen oder Veranstaltungen kann das Programm von Vorteil sein, da gerade hier es häufig erwünscht ist, das Teilnehmer anonym bleiben und das Zensieren von Gesichtern bei großen Gruppen aufwändig sein kann.


# Verwendete Technologien

- Backend: Python mit Flask
- Frontend: HTML, CSS, JS
- API zur Gesichtserkennung: [face_recognition](https://github.com/ageitgey/face_recognition)
- Dependencies: Sichtbar in der environment files, diese werden über miniconda konfiguriert (Siehe [Starten über die Kommandozeile](#über-die-kommandozeile))



# Starten über die Kommandozeile

## Windows

### Einmalige Einrichtung

#### Miniconda installieren

1. Miniconda von der offiziellen Seite herunterladen:  
   [https://www.anaconda.com/docs/getting-started/miniconda/main](https://www.anaconda.com/docs/getting-started/miniconda/main)
2. Öffne das Terminal und navigiere in den **backend**-Ordner des Projekts:
   ```bash
   cd path\to\project\backend
   ```
3. Initialisierung ausführen:
   ```bash
   conda init
   ```
4. Terminal schließen und wieder öffnen, anschließend wieder in den **backend**-Ordner navigieren.
5. Installation überprüfen:
   ```bash
   conda --version
   ```
   Wenn eine Versionsnummer zurückgegeben wird, war die Installation erfolgreich.

#### Environment erstellen
1. Erstelle das Environment:
   ```bash
   conda env create -f environment-windows.yml
   ```
2. Überprüfen, ob es erstellt wurde:
   ```bash
   conda env list
   ```
   Das Environment **bildverpixelung** sollte nun aufgelistet sein.



### Programm ausführen
1. Inn den **backend**-Ordner navigieren:
   ```bash
   cd path\to\project\backend
   ```
2. Environment aktivieren:
   ```bash
   conda activate bildverpixelung
   ```
   Die Aktivierung erkennt man an der Anzeige `(bildverpixelung)` vor dem Pfad im Terminal:
   ```bash
   (bildverpixelung) C:\Users\...\Verpixelung\backend>
   ```

3. Programm ausführen:
   ```bash
   python -m api.app
   ```




## macOS / Linux

### Einmalige Einrichtung

#### Miniconda installieren

1. Installiere Miniconda entweder über den offiziellen Installer:  
   [https://www.anaconda.com/docs/getting-started/miniconda/main](https://www.anaconda.com/docs/getting-started/miniconda/main)  
   oder – falls **Homebrew** installiert ist (empfohlen) – über:
   ```bash
   brew install --cask miniconda
   ```
2. Öffne das Terminal und navigiere in den **backend**-Ordner des Projekts:
   ```bash
   cd path/to/project/backend
   ```
3. Initialisierung ausführen:
   ```bash
   conda init zsh
   ```
4. Terminal schließen und wieder öffnen, anschließend wieder in den **backend**-Ordner navigieren.
5. Installation überprüfen:
   ```bash
   conda --version
   ```
   Wenn eine Versionsnummer zurückgegeben wird, war die Installation erfolgreich.

#### Environment erstellen
1. Erstelle das Environment:
   ```bash
   conda env create -f environment-mac.yml
   ```
2. Überprüfen, ob es erstellt wurde:
   ```bash
   conda env list
   ```
   Das Environment **bildverpixelung** sollte nun aufgelistet sein.



### Programm ausführen
1. In den **backend**-Ordner navigieren:
   ```bash
   cd path/to/project/backend
   ```
2. Environment aktivieren:
   ```bash
   conda activate bildverpixelung
   ```
3. Programm ausführen:
   ```bash
   python -m api.app
   ```
   
---


# Starten über das Executable
-  Lade das passende Executable für dein Betriebssystem herunter.
- Falls das System die Ausführung blockiert:
    - **macOS:** Öffne das Programm einmal, gehe in *Systemeinstellungen → Datenschutz & Sicherheit* und klicke bei der Meldung auf **"Trotzdem öffnen"**.
- Das Programm startet automatisch, das Frontend öffnet sich im Browser.

---

## CLI-Anwendung — Bildanalyse & Zensur
Die Anwendung lässt sich auch vollständig als Kommandozeilenanwendung (CLI) verwenden, hierbei werden sowohl einzelne Datein als auch Ordner unterstützt.


---

Um das CLI verwenden zu können muss vorher Miniconda eingerichtet werden, hierfür siehe:
- Windows: [Einmalige Einrichtung](#einmalige-einrichtung)
- macOS / Linux: [Einmalige Einrichtung](#einmalige-einrichtung-1)


## CLI ausführen

Navigiere im Terminal in den `backend`-Ordner und aktiviere das Environment:

```bash
conda activate bildverpixelung
```

Nun können Befehle in der vorgegebenen Struktur ausgeführt werden um die Anwendung zu benutzen.
Die grundlegende Struktur ist hierbei:
```bash
python -m cli.main <input> [Parameter]
```

---

## Command-Struktur

```bash
python -m cli.main INPUT [--mode MODE] [--censor TYPE] [--output ORDNER]
```

| Parameter  | Beschreibung                              |
|-------------|--------------------------------------------|
| `INPUT`     | Bilddatei oder Ordner mit Bildern          |
| `--mode`    | Modus der Ausführung (`detect` oder `censor`) |
| `--censor`  | Art der Zensur (`pixel`, `blur`, `eyeBar`) |
| `--output`  | Optionaler Ausgabeordner                   |

---

## Parameter im Detail

### INPUT

Pfad zu einer **Bilddatei oder einem Ordner mit Bildern**.  
Unterstützte Formate: `.png`, `.jpg`, `.jpeg`, `.webp`

**Beispiel (ein Bild)**
```bash
python -m cli.main foto.jpg [Parameter]
```

**Beispiel (ganzer Ordner)**
```bash
python -m cli.main ./bilder [Parameter]
```

Alle Bilder im Ordner werden automatisch verarbeitet.

---

## Mode-Parameter

```bash
--mode detect
```
oder
```bash
--mode censor
```

### detect

- Erkennt Gesichter oder Augen im Bild
- Gibt die **Koordinaten der Detektionen** aus
- Verändert das Bild **nicht**

**Beispiel:**
```bash
python -m cli.main foto.jpg --mode detect [Parameter]
```

---

### censor

- Erkennt automatisch das passende Objekt
- Wendet Zensur auf das Bild an
- Speichert das Ergebnis als neue Datei

**Beispiel:**
```bash
python -m cli.main foto.jpg --mode censor [Parameter]
```

---

## Censor-Parameter

```bash
--censor pixel
--censor blur
--censor eyeBar
```

| Option    | Beschreibung                                   |
|------------|------------------------------------------------|
| `pixel`    | Verpixelung des Gesichts                       |
| `blur`     | Verwischen des Gesichts                        |
| `eyeBar`   | Fügt einen schwarzen Balken über die Augen ein |

**Standard:** `pixel`

---

## Automatische Objektauswahl

Die CLI wählt automatisch das **optimale Detektionsziel** basierend auf dem Zensurmodus.

| Zensurmodus | Detektiertes Objekt |
|--------------|--------------------|
| `pixel`      | Gesicht            |
| `blur`       | Gesicht            |
| `eyeBar`     | Augen              |

---

## Output-Parameter

```bash
--output ORDNER
```

Gibt optional den Ausgabeordner an.

**Beispiel:**
```bash
python -m cli.main foto.jpg --mode censor --output ./results
```

Wenn kein Output-Ordner angegeben wird, wird das Ergebnis im **gleichen Ordner wie das Inputbild** gespeichert.

---

## Mehrere Bilder verarbeiten

Die CLI kann ganze Ordner automatisch verarbeiten.

**Beispiel:**
```bash
python -m cli.main ./bilder --mode censor --censor pixel
```
