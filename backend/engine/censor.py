# Konkrete Implementierung der Anonymisierungsmethoden 
import base64
from PIL import Image
import io
import numpy as np
import math
from scipy.ndimage import gaussian_filter

def rotated_rect_points(cx, cy, width, height, angle):
                c = math.cos(angle)
                s = math.sin(angle)

                rect = []

                hw = width / 2
                hh = height / 2

                for iy in range(int(-hh), int(hh) + 1):
                    for ix in range(int(-hw), int(hw) + 1):

                        x = ix * c - iy * s + cx
                        y = ix * s + iy * c + cy

                        rect.append((round(x)-1, round(y)))
                        rect.append((round(x), round(y)))
                        rect.append((round(x)+1, round(y)))
                return rect
            


def censor(image: np.ndarray, boxes: list, mode = 'pixel', num_pixelation_x = 7, num_pixelation_y = 7) -> np.ndarray:
    """returns censored image given to the function according to the given boxes

    Args:
        image (np.ndarray): Bild, dass zensiert werden soll
        boxes (list): Liste der zu zensierenden Boxen
        mode (str, optional): Zensier modus, standardmäßig 'pixel'
        num_pixelation_x (int, optional): Menge an Pixeln auf die runter Zensiert wird (x)
        num_pixelation_y (int, optional): Menge an Pixeln auf die runter Zensiert wird (y)

    Returns:
        np.ndarray: censored image
    """

    output = image.copy()
    if mode != 'eyeBar':
        for box in boxes:
            # Koordinaten der Box so umwandeln, dass sie linke obere und rechte untere ecke angeben können
            box_left = box[0] - box[2]
            box_right = box[0] + box[2]
            box_up = box[1] - box[3]
            box_down = box[1] + box[3]  

            # Ab hier: Entscheidungsstruktur nach Art der Anonymisierung (eigentlich noch geplant: Gaußian Blur)
            if mode == 'pixel':
                # Variable 'Block' bezieht sich auf das, was zu einem Pixel wird. 'Box' bezieht sich auf den ganzen Bereich des erkannten Gesichtes
            
                # Größe der "Pixel-Blöcke" berechnen
                width_block_pix = (box_right - box_left) // num_pixelation_x
                height_block_pix = (box_down - box_up) // num_pixelation_y
                #Aufteilen in Blöcke (Erstellen je eines Blockes, fängt bei 0 an, Schrittgröße height/ width_block_pix, macht so viele Schritte bis Rand erreicht)
                for y in range(box_up, box_down, height_block_pix):
                    for x in range(box_left, box_right, width_block_pix):
                        #Block ausschneiden (array slicing)
                        block = image[y:y+height_block_pix, x:x+width_block_pix]

                        # Mittelwert berechnen (axis=(0,1) bedeutet Mittelwert über Zeilen UND Spalten) => Ergebnis: Vektor der Länge 3 (Je Mittelwert für R-/G-/B-Wert)
                        mean_color = block.mean(axis=(0, 1)).astype(np.uint8) #Zusatz um Mittelwerte (float) zu Ganzzahlen (0-255) umzuwandeln

                        # Mittelwert allen Pixeln im Block zuweisen => überschreiben aller Pixel im Block
                        output[y:y+height_block_pix, x:x+width_block_pix] = mean_color
            elif mode == 'blur': #Aus Zeitmangel konnten wir diesen algorithmus nicht mehr selber implementieren, dahingehend wird dieser importiert (scipy)
                region = output[box_up:box_down, box_left:box_right].astype(np.float32)
                # Apply Gaussian blur to each color channel separately
                for c in range(3):  # R, G, B channels
                    region[:,:,c] = gaussian_filter(region[:,:,c], sigma=10) #häherer sigmaa Wert -> Stärkerer Blur
                output[box_up:box_down, box_left:box_right] = region.astype(np.uint8)

    else:
        for eyePair in boxes: # eyePair ist nicht wie bei der Verpixelung eine box, sondern eine Liste aus zwei boxen (zwei Augen). Die erste Box ist das linkere Auge.
            # Liste von allen Ecken des linken und rechten Auges, beginnend in der oberen linken Ecke, im Uhrzeigersinn
            lWidth, lHeight = eyePair[0][2:]

            rWidth, rHeight = eyePair[1][2:]

            lCorners =  [(eyePair[0][0]-lWidth,  eyePair[0][1]-lHeight), (eyePair[0][0] + lWidth, eyePair[0][1] - lHeight), (eyePair[0][0] + lWidth, eyePair[0][1] + lHeight), (eyePair[0][0]-lWidth, eyePair[0][1] + lHeight)]
            rCorners = [(eyePair[1][0]-rWidth,  eyePair[1][1]-rHeight), (eyePair[1][0] + rWidth, eyePair[1][1]-rHeight), (eyePair[1][0] + rWidth, eyePair[1][1]+ rHeight), (eyePair[1][0]-rWidth, eyePair[1][1] + rHeight)]
            # 1. von welchen Ecken aus muss die Bar gezogen werden? (entweder linksoben bis rechtsunten oder linksunten bis rechtsoben)
            if eyePair[0][1] <= eyePair[1][1]: #right eye lower
                lCorner = (lCorners[0]) #linkester, höchster Punkt
                adjacentlCorners = [lCorners[1], lCorners[3]] #die Ecken, die an die "extremste" Ecke (lCorner) angrenzen. Erste Ecke ist die obere, zweite die niedrigere
                rCorner = (rCorners[2]) #rechtester, niedrigster Punkt
                adjacentrCorners = [rCorners[1], rCorners[3]]
            else: #right eye higher
                lCorner = (lCorners[3]) #linkester, niedrigster Punkt
                adjacentlCorners = [lCorners[0], lCorners[2]] 
                rCorner = (rCorners[1]) #rechtester, höchster Punkt
                adjacentrCorners = [rCorners[0], rCorners[2]]
            
            # 2. Winkel und mittelpunkt berechnen

            lCornCenter = ((adjacentlCorners[0][0] + adjacentlCorners[1][0])/2, (adjacentlCorners[0][1] + adjacentlCorners[1][1])/2)
            rCornCenter = ((adjacentrCorners[0][0] + adjacentrCorners[1][0])/2, (adjacentrCorners[0][1] + adjacentrCorners[1][1])/2)
            
            rectCenter = ((rCornCenter[0] + lCornCenter[0])/2, (rCornCenter[1] + lCornCenter[1])/2)

            rectAngle = math.atan2(rCornCenter[1] - lCornCenter[1], rCornCenter[0] - lCornCenter[0]) # in rad

            # 3. Breite (zwischen beiden Augen) des Rechtecks bestimmen: der Abstand, zwischen einem punkt, der zwar die gleiche Höhe hat wie die lcorner, aber eine kleinere

            rCentCornAngle = math.atan2(abs(rCorner[1]-rectCenter[1]), abs(rCorner[0] - rectCenter[0]))
            rCentCornDist = math.sqrt((rCorner[0]-rectCenter[0])**2+(rCorner[1]-rectCenter[1])**2)
            rDiagonalWidth = rCentCornDist/math.cos(abs(rCentCornAngle)-abs(rectAngle))

            lCentCornAngle = math.atan2(abs(lCorner[1]-rectCenter[1]), abs(lCorner[0] - rectCenter[0]))
            lCentCornDist = math.sqrt((lCorner[0]-rectCenter[0])**2+(lCorner[1]-rectCenter[1])**2)
            lDiagonalWidth = lCentCornDist/math.cos(abs(lCentCornAngle) - abs(rectAngle))

            width = max(rDiagonalWidth,lDiagonalWidth)*2 # damit beide rects immer abgedeckt sind

            # 4. Höhe berechnen: max aus distance zwischen corner centers
            height = 0
            
            for i in range(len(adjacentrCorners)): # immer 2 mal
                newHeight = math.sqrt((rCornCenter[0]-adjacentrCorners[i][0])**2 + (rCornCenter[1]-adjacentrCorners[i][1])**2)
                height = max(newHeight, height) 

            for i in range(len(adjacentlCorners)): # immer 2 mal
                newHeight = math.sqrt((lCornCenter[0]-adjacentlCorners[i][0])**2 + (lCornCenter[1]-adjacentlCorners[i][1])**2)
                height = max(newHeight, height) 

            # for i in range(len(adjacentlCorners)): # immer 2 mal
            #     newHeight = math.sqrt((lCornerAdjusted[0]-adjacentlCorners[i][0])**2 + (lCornerAdjusted[1]-adjacentlCorners[i][1])**2)
            #     height = max(newHeight, height)
            
            height = height*2 # weil die rectangle funktion die height selbst halbiert

            #Größe der Balken hiermit noch mal anpassen
            width *= 1.8
            height *= 1.5

            # 5. Rechtecks-koordinaten berechnen
            rect = rotated_rect_points(rectCenter[0], rectCenter[1], width, height, rectAngle)

            # 6. Bild bearbeiten
            for x,y in rect:
                try:
                    output[y][x] = [0,0,0]
                except:
                    print('tried to blacken out of frame pixel')



    #Frage: wie Bild zurückgeben? Wie handeln, dass nur ein Teil verpixelt werden soll? (Lösung: nicht bei 0 anfangen? Eig. Wäre Funktion, die Anfangswert als Parameter kriegt besser)
    # wie mehrere Gesichter handeln?     
    return output.astype(np.uint8)
