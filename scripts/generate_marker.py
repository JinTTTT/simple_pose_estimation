import cv2
from pathlib import Path

MARKER_ID = 42
MARKER_DICT = cv2.aruco.DICT_6X6_250
IMAGE_SIZE_PX = 600
MARKER_SIZE_M = 0.174
BORDER_PX = 40
ROOT_DIR = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT_DIR / "images" / "targets" / f"marker_6x6_id{MARKER_ID}.png"

dictionary = cv2.aruco.getPredefinedDictionary(MARKER_DICT)
marker_image = cv2.aruco.generateImageMarker(dictionary, MARKER_ID, IMAGE_SIZE_PX)

marker_image = cv2.copyMakeBorder(
    marker_image,
    BORDER_PX, BORDER_PX, BORDER_PX, BORDER_PX,
    cv2.BORDER_CONSTANT, value=255
)

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
cv2.imwrite(str(OUT_PATH), marker_image)
print(f"Saved marker ID={MARKER_ID}, physical size={MARKER_SIZE_M}m to {OUT_PATH}")
