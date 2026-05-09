import time
from pathlib import Path

import cv2
import numpy as np


CAMERA_INDEX = 2
ROOT_DIR = Path(__file__).resolve().parents[1]
CALIBRATION_FILE = ROOT_DIR / "config" / "camera_calibration.yaml"

MARKER_ID = 42
MARKER_SIZE_M = 0.174
ARUCO_DICT = cv2.aruco.DICT_6X6_250


def load_camera_calibration(path):
    fs = cv2.FileStorage(str(path), cv2.FILE_STORAGE_READ)
    if not fs.isOpened():
        raise RuntimeError(f"Could not open calibration file: {path}")

    camera_matrix = fs.getNode("camera_matrix").mat()
    distortion_coefficients = fs.getNode("distortion_coefficients").mat()
    fs.release()

    if camera_matrix is None or distortion_coefficients is None:
        raise RuntimeError(f"Could not read K and D from: {path}")

    return camera_matrix, distortion_coefficients


def make_marker_object_points(marker_size_m):
    half_size = marker_size_m / 2.0

    # Same corner order returned by ArUco: top-left, top-right, bottom-right, bottom-left.
    return np.array(
        [
            [-half_size, -half_size, 0.0],
            [half_size, -half_size, 0.0],
            [half_size, half_size, 0.0],
            [-half_size, half_size, 0.0],
        ],
        dtype=np.float32,
    )


def make_cube_object_points(cube_size_m):
    half_size = cube_size_m / 2.0

    # The bottom face lies on the marker plane: z = 0.
    # The top face goes "out of" the marker plane: z = -cube_size_m.
    return np.array(
        [
            [-half_size, -half_size, 0.0],
            [half_size, -half_size, 0.0],
            [half_size, half_size, 0.0],
            [-half_size, half_size, 0.0],
            [-half_size, -half_size, -cube_size_m],
            [half_size, -half_size, -cube_size_m],
            [half_size, half_size, -cube_size_m],
            [-half_size, half_size, -cube_size_m],
        ],
        dtype=np.float32,
    )


def draw_cube(frame, image_points):
    points = image_points.reshape(-1, 2).astype(int)

    bottom_edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
    top_edges = [(4, 5), (5, 6), (6, 7), (7, 4)]
    vertical_edges = [(0, 4), (1, 5), (2, 6), (3, 7)]

    for start, end in bottom_edges:
        cv2.line(frame, points[start], points[end], (255, 0, 0), 2)

    for start, end in top_edges:
        cv2.line(frame, points[start], points[end], (0, 255, 0), 2)

    for start, end in vertical_edges:
        cv2.line(frame, points[start], points[end], (0, 0, 255), 2)


def main():
    camera_matrix, distortion_coefficients = load_camera_calibration(CALIBRATION_FILE)

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera {CAMERA_INDEX}")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
    detector_parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, detector_parameters)

    marker_object_points = make_marker_object_points(MARKER_SIZE_M)
    cube_object_points = make_cube_object_points(MARKER_SIZE_M)

    print("Controls:")
    print("  q or Esc: quit")
    print(f"Looking for marker id: {MARKER_ID}")

    last_pose_print_time = 0.0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Could not read frame")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = detector.detectMarkers(gray)
        now = time.time()

        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)

            for marker_corners, marker_id in zip(corners, ids.flatten()):
                if marker_id != MARKER_ID:
                    continue

                image_points = marker_corners.reshape(4, 2).astype(np.float32)

                success, rvec, tvec = cv2.solvePnP(
                    marker_object_points,
                    image_points,
                    camera_matrix,
                    distortion_coefficients,
                )

                if not success:
                    continue

                cube_image_points, _ = cv2.projectPoints(
                    cube_object_points,
                    rvec,
                    tvec,
                    camera_matrix,
                    distortion_coefficients,
                )

                draw_cube(frame, cube_image_points)

                t = tvec.ravel()
                if now - last_pose_print_time > 1.0:
                    print(
                        f"marker position [m]: x={t[0]:.4f}, y={t[1]:.4f}, z={t[2]:.4f}",
                        flush=True,
                    )
                    last_pose_print_time = now

        cv2.imshow("Cube on ArUco marker", frame)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
