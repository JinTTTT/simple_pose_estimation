import os
from pathlib import Path

import cv2


CAMERA_INDEX = 2
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# OpenCV uses inner corners, not chessboard squares.
# Your printed board has 10 x 7 squares, so it has 9 x 6 inner corners.
CHESSBOARD_SIZE = (9, 6)

ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT_DIR / "images" / "calibration"


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera {CAMERA_INDEX}")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    saved_count = 0

    print("Controls:")
    print("  s: save image when chessboard corners are detected")
    print("  q or Esc: quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Could not read frame")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        found, corners = cv2.findChessboardCorners(gray, CHESSBOARD_SIZE)

        display = frame.copy()
        if found:
            cv2.drawChessboardCorners(display, CHESSBOARD_SIZE, corners, found)
            status = "FOUND - press s to save"
            color = (0, 255, 0)
        else:
            status = "NOT FOUND"
            color = (0, 0, 255)

        cv2.putText(
            display,
            status,
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2,
        )
        cv2.putText(
            display,
            f"saved: {saved_count}",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )

        cv2.imshow("Capture calibration images", display)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):
            break

        if key == ord("s"):
            if found:
                filename = os.path.join(OUTPUT_DIR, f"calib_{saved_count:02d}.png")
                cv2.imwrite(filename, frame)
                print(f"Saved {filename}")
                saved_count += 1
            else:
                print("Chessboard not detected, image not saved")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
