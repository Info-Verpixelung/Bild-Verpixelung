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



# CLI Anwendung -- Bildanalyse & Zensur

Die CLI ermöglicht es, Bilder automatisch auf **Gesichter oder Augen zu
analysieren** und diese optional zu **zensieren** (Pixeln, Blur oder
Eye-Bar).

Die Anwendung kann entweder ein **einzelnes Bild** oder einen **ganzen
Ordner mit Bildern** verarbeiten.

------------------------------------------------------------------------

# CLI ausführen

Im Terminal in den `backend` Ordner navigieren und das Environment
aktivieren.

``` bash
conda activate bildverpixelung
```

Danach kann die CLI gestartet werden mit:

``` bash
python -m cli.main <input> [OPTIONEN]
```

Beispiel:

``` bash
python -m cli.main image.jpg --mode censor --censor blur
```

------------------------------------------------------------------------

# Command Struktur

``` bash
python -m cli.main INPUT [--mode MODE] [--censor TYPE] [--output ORDNER]
```

Parameter    Beschreibung
  ------------ -----------------------------------------------
`INPUT`      Bilddatei oder Ordner mit Bildern
`--mode`     Modus der Ausführung (`detect` oder `censor`)
`--censor`   Art der Zensur (`pixel`, `blur`, `eyeBar`)
`--output`   Optionaler Ausgabeordner

------------------------------------------------------------------------

# Parameter im Detail

## INPUT

Pfad zu einer **Bilddatei oder einem Ordner mit Bildern**.

Unterstützte Formate:

-   `.png`
-   `.jpg`
-   `.jpeg`
-   `.webp`

### Beispiel (ein Bild)

``` bash
python -m cli.main foto.jpg
```

### Beispiel (ganzer Ordner)

``` bash
python -m cli.main ./bilder
```

Alle Bilder im Ordner werden automatisch verarbeitet.

------------------------------------------------------------------------

# Mode Parameter

``` bash
--mode detect
```

oder

``` bash
--mode censor
```

## detect

-   Erkennt Gesichter oder Augen im Bild
-   Gibt nur die **Koordinaten der Detektionen** aus
-   Bild wird **nicht verändert**

Beispiel:

``` bash
python -m cli.main foto.jpg --mode detect
```

------------------------------------------------------------------------

## censor

-   Erkennt automatisch das passende Objekt
-   Wendet Zensur auf das Bild an
-   Speichert das Ergebnis als neue Datei

Beispiel:

``` bash
python -m cli.main foto.jpg --mode censor
```

------------------------------------------------------------------------

# Censor Parameter

``` bash
--censor pixel
--censor blur
--censor eyeBar
```

Option     Beschreibung
  ---------- ---------------------------------
`pixel`    Pixelisiert das Gesicht
`blur`     Verwischt das Gesicht
`eyeBar`   Schwarzer Balken über den Augen

Standardwert:

    pixel

------------------------------------------------------------------------

# Automatische Subject Auswahl

Die CLI wählt automatisch das **optimale Detektionsziel** basierend auf
dem Zensurmodus.

Zensurmodus   Detektiertes Objekt
  ------------- ---------------------
`pixel`       Gesicht
`blur`        Gesicht
`eyeBar`      Augen

------------------------------------------------------------------------

# Output Parameter

``` bash
--output ORDNER
```

Optionaler Ordner für die Ausgabe.

Beispiel:

``` bash
python -m cli.main foto.jpg --mode censor --output ./results
```

Wenn kein Output angegeben wird:

-   Bild wird im **gleichen Ordner wie das Inputbild** gespeichert.

------------------------------------------------------------------------

# Mehrere Bilder verarbeiten

Die CLI kann ganze Ordner automatisch verarbeiten.

Beispiel:

``` bash
python -m cli.main ./bilder --mode censor --censor pixel
```

