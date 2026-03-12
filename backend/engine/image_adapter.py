# definiert Methoden, wie PILs in NumPy arrays umgewandelt werden können und anders herum
import numpy as np
from PIL import Image

def piltonp(image: Image.Image) -> np.ndarray:
    """
    Convert a PIL Image to a NumPy array (H x W x 3, uint8, RGB).
    """
    if image.mode != "RGB":
        image = image.convert("RGB")
    arr = np.array(image)  # shape: (H, W, 3 [also dreidimensionales array, mit Höhe, Breite und Farbkanal (RGB) als Indexes/ Dimensionen]), dtype=uint8
    return arr

def nptopil(array: np.ndarray) -> Image.Image:
    """
    Convert a NumPy image array (H x W x 3, uint8) back to a PIL Image.
    """
    if array.dtype != np.uint8:
        array = array.astype(np.uint8)
    image = Image.fromarray(array, mode="RGB")
    return image
