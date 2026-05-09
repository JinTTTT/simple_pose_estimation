import cv2
import numpy as np
import time
from pathlib import Path


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
    object_points = np.array(
        [
            [-half_size, -half_size, 0.0],
            [half_size, -half_size, 0.0],
            [half_size, half_size, 0.0],
            [-half_size, half_size, 0.0],
        ],
        dtype=np.float32,
    )

    return object_points


def main():
    # Step 1: load camera calibration.
    camera_matrix, distortion_coefficients = load_camera_calibration(CALIBRATION_FILE)

    print("Camera matrix K:")
    print(camera_matrix)
    print()
    print("Distortion coefficients D:")
    print(distortion_coefficients.ravel())
    print()

    # Step 2: open camera.
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera {CAMERA_INDEX}")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Step 3: create ArUco detector.
    dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
    detector_parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, detector_parameters)

    # These are the known 3D corner positions of your physical marker.
    object_points = make_marker_object_points(MARKER_SIZE_M)

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

        # Step 4: detect ArUco markers and get their image corners.
        corners, ids, _ = detector.detectMarkers(gray)
        now = time.time()

        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)

            for marker_corners, marker_id in zip(corners, ids.flatten()):
                if marker_id != MARKER_ID:
                    continue

                image_points = marker_corners.reshape(4, 2).astype(np.float32)

                # Step 5: solvePnP estimates marker pose in the camera frame.
                success, rvec, tvec = cv2.solvePnP(
                    object_points,
                    image_points,
                    camera_matrix,
                    distortion_coefficients,
                )

                if not success:
                    continue

                cv2.drawFrameAxes(
                    frame,
                    camera_matrix,
                    distortion_coefficients,
                    rvec,
                    tvec,
                    MARKER_SIZE_M * 0.5,
                )

                t = tvec.ravel()
                r_degrees = np.degrees(rvec.ravel())

                if now - last_pose_print_time > 1.0:
                    print(
                        f"tvec in camera frame [m]: x={t[0]:.4f}, y={t[1]:.4f}, z={t[2]:.4f}",
                        flush=True,
                    )
                    print(
                        "rvec [deg]: "
                        f"rx={r_degrees[0]:.2f}, ry={r_degrees[1]:.2f}, rz={r_degrees[2]:.2f}",
                        flush=True,
                    )
                    print(flush=True)
                    last_pose_print_time = now

                cv2.putText(
                    frame,
                    f"t: x={t[0]:.3f} y={t[1]:.3f} z={t[2]:.3f} m",
                    (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )
                cv2.putText(
                    frame,
                    f"r: {r_degrees[0]:.1f}, {r_degrees[1]:.1f}, {r_degrees[2]:.1f} deg",
                    (20, 65),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )

        cv2.imshow("ArUco pose from camera", frame)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
