# Konkrete Implementierung der Anonymisierungsmethoden 
import base64
from PIL import Image
import io
import numpy as np
import math

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
            


def censor(image: np.ndarray, boxes: list, mode = 'pixel', num_pixelation_x = 10, num_pixelation_y = 10) -> np.ndarray:
    """returns censored image given to the function according to the given boxes

    Args:
        image (np.ndarray): the image to censor
        boxes (list): A list of boxes with areas to censor
        mode (str, optional): Pixelation method. Defaults to 'pixel'.
        num_pixelation_x (int, optional):amount of pixels for 'pixel' censor. Defaults to 10.
        num_pixelation_y (int, optional):amount of pixels for 'pixel' censor. Defaults to 10.

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

            # Ab hier: Entscheidungsstruktur nach Art der Anonymisierung (neigentlich noch geplant: Gaußian Blur)
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

            # 5. Rechtecks-koordinaten berechnen
            rect = rotated_rect_points(rectCenter[0], rectCenter[1], width, height, rectAngle)

            # 6. Bild bearbeiten
            for x,y in rect:
                try:
                    output[y][x] = [0,0,0]
                except:
                    print('tried to blacken out of frame pixel')
            
            # cx1 = round((lCorners[0][0]+lCorners[2][0])/2)
            # cy1 = round((lCorners[0][1]+lCorners[2][1])/2)
            # totalWidth= lCorners[2][0]-lCorners[0][0]
            # totalHeight= (lCorners[2][1]-lCorners[0][1])
            # liste = rotated_rect_points(cx1, cy1, totalWidth, totalHeight,0)
            # for point in liste:
            #     output[point[1]][point[0]] = [255,0,0]
                    
            # cx1 = round((rCorners[0][0]+rCorners[2][0])/2)
            # cy1 = round((rCorners[0][1]+rCorners[2][1])/2)
            # totalWidth= rCorners[2][0]-rCorners[0][0]
            # totalHeight= (rCorners[2][1]-rCorners[0][1])
            # liste = rotated_rect_points(cx1, cy1, totalWidth, totalHeight,0)
            # for point in liste:
            #     output[point[1]][point[0]] = [255,0,0]
            
            # output[round(rectCenter[1])][round(rectCenter[0])] = [0,255,0]
            # output[round(lCornCenter[1])][round(lCornCenter[0])] = [0,255,0]
            # output[round(rCornCenter[1])][round(rCornCenter[0])] = [0,255,0]               
            
            


    #Frage: wie Bild zurückgeben? Wie handeln, dass nur ein Teil verpixelt werden soll? (Lösung: nicht bei 0 anfangen? Eig. Wäre Funktion, die Anfangswert als Parameter kriegt besser)
    # wie mehrere Gesichter handeln?     
    return output.astype(np.uint8)

if '__name__' == "__main__": # TODO wenn dieses Programm an sich ausgeführt wird, dann wird nicht probiert, app.py auszuführen
    data_url = "data:image/jpeg;base64,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"
    print("test")
    base64_string = data_url.split(",")[1]
    image_bytes = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_bytes)) 
    width, height = image.size
    print(f"Bildgröße: {width}x{height}")
    image_array = np.array(image)
    #print(image_array)
    img = Image.fromarray(censor(image_array, [[[70, 100, 15, 10],[140, 50, 10, 10]]], 'eyeBar'))
    img.show()


    #print(image_array[0])
