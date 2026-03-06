# Hintergrundwissen über Anonymisierungsmethoden & ihre Sicherheit 
hier ist ein bisschen theoretischer Hintergrund zu Anonymisierungen & ihrer Sicherheit in den Zeiten von KI gesammelt 

## Überblick über verschiedene Anonymisierungsmethoden: 
Die, deren Implementierung ursprünglich geplant war sind rot umkreist 
![grafische Darstellung_Verpixelungsmethoden](screenshots/grafische_Darstellung_Verpixelungsmethoden.png)

## Überblick über ihre Sicherheit: 
Daten basierend auf einer Studie, in der Wissenschaftler eine KI trainiert haben, die anonymisierte Bilder erst versucht, zu "rekonstruieren", um dann eine Gesichtserkennung durchzuführen
![Sicherheit_Verpixelungsmethoden](screenshots/Sicherheit_Verpixelungsmethoden.png)

## Auswertung: 
Gaussian Blur sehr unsicher, kann mit einer 90-100 % igen Genauigkeit umgekehrt werden 
Schwarzer Balken semi sicher, kann mit Genauigkeit von ca. 20% umgekehrt werden 
Pixelation von den drei am Sichersten, kann mit Genauigkeit von ca. 10% umgekehrt werden (in Studie: 16x16 Pixel) 
=> alle drei Methoden nicht so super 

sicherste Methode: k same eigen 
=> weitere Recherche dazu folgt 

## So sahen übrigens die Deanonymisierten Bilder aus 
Nur falls es jemanden interssiert, ist ganz spannend 
![Deanonymisierte_Bilder](screenshots/Deanonymisierte_Bilder.png)

Quelle: 
https://arxiv.org/pdf/2210.10651


