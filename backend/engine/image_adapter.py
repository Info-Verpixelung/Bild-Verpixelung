# backend/engine/imageadapter.py
import numpy as np
from PIL import Image

def piltonp(image: Image.Image) -> np.ndarray:
    """
    Convert a PIL Image to a NumPy array (H x W x 3, uint8, RGB).
    """
    if image.mode != "RGB":
        image = image.convert("RGB")
    arr = np.array(image)  # shape: (H, W, 3), dtype=uint8
    return arr


def nptopil(array: np.ndarray) -> Image.Image:
    """
    Convert a NumPy image array (H x W x 3, uint8) back to a PIL Image.
    """
    if array.dtype != np.uint8:
        array = array.astype(np.uint8)
    # If needed you could also ensure shape is 3 channels,
    # but for your pipeline H x W x 3 is expected.
    image = Image.fromarray(array, mode="RGB")
    return image
