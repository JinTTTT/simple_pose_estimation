import cv2
import numpy as np
import os
import json

# ---------- config ----------
MARKER_IMG_PATH = "marker_6x6_id42.png"
MARKER_SIZE_M   = 0.1       # physical side length of the marker square
MARKER_IMAGE_PX = 600       # must match generate_marker.py
BORDER_PX       = 40        # must match generate_marker.py
IMG_W, IMG_H    = 640, 480
OUTPUT_DIR      = "simulated_views"

# ---------- virtual camera intrinsics ----------
# K is the 3x3 camera matrix:
#   fx, fy : focal lengths in pixels (how "zoomed in" the lens is)
#   cx, cy : principal point = image center
# We invent a reasonable camera — no real hardware needed.
K = np.array([[600.,   0., IMG_W / 2.],
              [  0., 600., IMG_H / 2.],
              [  0.,   0.,         1.]], dtype=np.float64)
dist_coeffs = np.zeros(5)   # assume no lens distortion

# ---------- marker geometry ----------
# The marker sits flat at Z=0, centered at the world origin.
# These are the 4 corners in 3D world coordinates.
# Order: top-left, top-right, bottom-right, bottom-left  (OpenCV ArUco convention)
s = MARKER_SIZE_M / 2.
obj_pts = np.array([[-s, -s, 0.],
                    [ s, -s, 0.],
                    [ s,  s, 0.],
                    [-s,  s, 0.]], dtype=np.float64)

# Pixel coordinates of the same 4 corners inside the saved marker image
p, q = BORDER_PX, BORDER_PX + MARKER_IMAGE_PX
src_corners = np.float32([[p, p], [q, p], [q, q], [p, q]])

# ---------- ground truth poses ----------
# Each pose = (rotation in degrees [rx, ry, rz], translation in meters [tx, ty, tz])
# The camera looks at the marker from different angles.
# rx/ry/rz are Euler-style rotation angles fed into cv2 as a Rodrigues vector.
poses_deg = [
    ([  0,   0, 0], [0.0, 0.0, 0.5]),   # straight on,    0.5 m away
    ([  0,  30, 0], [0.0, 0.0, 0.5]),   # rotated 30° Y,  0.5 m away
    ([ 30,   0, 0], [0.0, 0.0, 0.5]),   # rotated 30° X,  0.5 m away
    ([ 20,  20, 0], [0.0, 0.0, 0.5]),   # combined tilt,  0.5 m away
    ([ 15, -25, 0], [0.0, 0.0, 0.8]),   # combined tilt,  0.8 m away
]

# ---------- simulate ----------
os.makedirs(OUTPUT_DIR, exist_ok=True)
marker_img = cv2.imread(MARKER_IMG_PATH, cv2.IMREAD_GRAYSCALE)

ground_truth = {"camera_matrix": K.tolist(), "views": {}}

for i, (deg, t) in enumerate(poses_deg):
    rvec = np.radians(deg, dtype=np.float64)
    tvec = np.array(t, dtype=np.float64)

    # Project the 4 3D corners onto the virtual camera image plane
    dst_corners, _ = cv2.projectPoints(obj_pts, rvec, tvec, K, dist_coeffs)
    dst_corners = dst_corners.reshape(-1, 2).astype(np.float32)

    # Homography maps marker image pixels → projected pixel positions
    # (valid because the marker is a flat plane)
    H, _ = cv2.findHomography(src_corners, dst_corners)

    # Warp the marker image into an output canvas using that homography
    output = cv2.warpPerspective(marker_img, H, (IMG_W, IMG_H), borderValue=200)

    out_path = os.path.join(OUTPUT_DIR, f"view_{i:02d}.png")
    cv2.imwrite(out_path, output)

    ground_truth["views"][f"view_{i:02d}"] = {"rvec_deg": deg, "tvec_m": t}
    print(f"[view {i:02d}]  rot={deg} deg   t={t} m")

with open(os.path.join(OUTPUT_DIR, "ground_truth.json"), "w") as f:
    json.dump(ground_truth, f, indent=2)

print(f"\nSaved {len(poses_deg)} views + ground_truth.json → {OUTPUT_DIR}/")
