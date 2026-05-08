import cv2

MARKER_ID = 42
MARKER_DICT = cv2.aruco.DICT_6X6_250
IMAGE_SIZE_PX = 600
MARKER_SIZE_M = 0.1          # physical size in meters (used in pose estimation)
BORDER_PX = 40

dictionary = cv2.aruco.getPredefinedDictionary(MARKER_DICT)
marker_image = cv2.aruco.generateImageMarker(dictionary, MARKER_ID, IMAGE_SIZE_PX)

marker_image = cv2.copyMakeBorder(
    marker_image,
    BORDER_PX, BORDER_PX, BORDER_PX, BORDER_PX,
    cv2.BORDER_CONSTANT, value=255
)

cv2.imwrite("marker_6x6_id42.png", marker_image)
print(f"Saved marker ID={MARKER_ID}, physical size={MARKER_SIZE_M}m")
