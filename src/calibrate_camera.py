import glob
import os
from pathlib import Path

import cv2
import numpy as np


ROOT_DIR = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT_DIR / "images" / "calibration"
OUTPUT_FILE = ROOT_DIR / "config" / "camera_calibration.yaml"

# Your printed board has 10 x 7 squares, so OpenCV sees 9 x 6 inner corners.
CHESSBOARD_SIZE = (9, 6)

# Measured square size: 23.5 mm = 0.0235 m.
SQUARE_SIZE_M = 0.0235


def make_object_points():
    objp = np.zeros((CHESSBOARD_SIZE[0] * CHESSBOARD_SIZE[1], 3), np.float32)
    objp[:, :2] = np.mgrid[
        0 : CHESSBOARD_SIZE[0],
        0 : CHESSBOARD_SIZE[1],
    ].T.reshape(-1, 2)
    objp *= SQUARE_SIZE_M
    return objp


def main():
    image_paths = sorted(glob.glob(os.path.join(IMAGE_DIR, "*.png")))
    if not image_paths:
        raise RuntimeError(f"No PNG images found in {IMAGE_DIR}")

    objp = make_object_points()

    object_points = []
    image_points = []
    image_size = None

    criteria = (
        cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
        30,
        0.001,
    )

    print(f"Reading {len(image_paths)} calibration images...")

    for path in image_paths:
        image = cv2.imread(path)
        if image is None:
            print(f"[skip] could not read {path}")
            continue

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image_size = (gray.shape[1], gray.shape[0])

        found, corners = cv2.findChessboardCorners(gray, CHESSBOARD_SIZE)
        if not found:
            print(f"[skip] chessboard not found: {path}")
            continue

        refined_corners = cv2.cornerSubPix(
            gray,
            corners,
            winSize=(11, 11),
            zeroZone=(-1, -1),
            criteria=criteria,
        )

        object_points.append(objp)
        image_points.append(refined_corners)
        print(f"[use ] {path}")

    if len(object_points) < 10:
        raise RuntimeError(
            f"Only {len(object_points)} valid images. Capture more good chessboard views."
        )

    # rms is reprojection error in pixels.
    rms_error, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
        object_points,
        image_points,
        image_size,
        None,
        None,
    )

    print()
    print("Calibration result")
    print("------------------")
    print(f"valid images: {len(object_points)} / {len(image_paths)}")
    print(f"image size: {image_size[0]} x {image_size[1]}")
    print(f"RMS reprojection error: {rms_error:.4f} pixels")
    print()
    print("camera_matrix K:")
    print(camera_matrix)
    print()
    print("distortion_coefficients D:")
    print(dist_coeffs.ravel())

    fs = cv2.FileStorage(str(OUTPUT_FILE), cv2.FILE_STORAGE_WRITE)
    fs.write("image_width", image_size[0])
    fs.write("image_height", image_size[1])
    fs.write("chessboard_inner_corners_x", CHESSBOARD_SIZE[0])
    fs.write("chessboard_inner_corners_y", CHESSBOARD_SIZE[1])
    fs.write("square_size_m", SQUARE_SIZE_M)
    fs.write("rms_reprojection_error", rms_error)
    fs.write("camera_matrix", camera_matrix)
    fs.write("distortion_coefficients", dist_coeffs)
    fs.release()

    print()
    print(f"Saved calibration to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
