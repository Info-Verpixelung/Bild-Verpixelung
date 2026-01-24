# TODOS

 - [x] Hochgeladene Fotos einzeln löschbar machen (im preview fenster)
 - [x] beim Hochladen von bildern **keine** bereits hochgeladenen löschen/überschreiben sowohl im hochlade fenster als auch im preview fenster
 - [x] Dark/Light mode switch sichtbarer machen / Beschreibung geben (PS: vollkommen unnötige Zeitverschwendung aber sieht gut aus :'))
 - [x] Bilder werden hochgeladen egal wohin man sie zieht auf der Seite
 - [x] Unfassbar nerviger bug (Text in den vorschau feldern verschwindet und kommt nicht wieder) fixen
 - [x] Hochgeladene Bilder sollten nicht verschwinden bei reload -> verursacht höchstwahrscheinlich den local storage error, kümmer ich mich später drum
 - [ ] local storage error (DOMException) lösen, tritt ab dem zweiten bild auf
 - [ ] (Für später): **Input validation von bildern** (sicherheitslücken vermeiden, anti memory-ressource exhaustion, prüfen dass auch wirklich **BILDER** hochgeladen wurden, upload Größe beschränken menge und größe der bilder insgesamt) **FALLS** das Projekt als website gehostet wird, extrem wichtig und potentiell angreifbar (gilt für alle requests außer "GET" aber *im Fall vom hosten Pentest unvermeidbar*)