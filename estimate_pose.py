import cv2
import numpy as np
import json
import os

# ---------- config ----------
MARKER_SIZE_M = 0.1
MARKER_DICT   = cv2.aruco.DICT_6X6_250
VIEWS_DIR     = "simulated_views"

# ---------- camera intrinsics (must match simulate_views.py) ----------
IMG_W, IMG_H = 640, 480
K = np.array([[600.,   0., IMG_W / 2.],
              [  0., 600., IMG_H / 2.],
              [  0.,   0.,         1.]], dtype=np.float64)
dist_coeffs = np.zeros(5)

# ---------- marker 3D corners in world frame (same as simulate_views.py) ----------
s = MARKER_SIZE_M / 2.
obj_pts = np.array([[-s, -s, 0.],
                    [ s, -s, 0.],
                    [ s,  s, 0.],
                    [-s,  s, 0.]], dtype=np.float64)

# ---------- ArUco detector ----------
dictionary = cv2.aruco.getPredefinedDictionary(MARKER_DICT)
detector   = cv2.aruco.ArucoDetector(dictionary, cv2.aruco.DetectorParameters())

# ---------- load ground truth ----------
with open(os.path.join(VIEWS_DIR, "ground_truth.json")) as f:
    ground_truth = json.load(f)

# ---------- process each view ----------
view_files = sorted(f for f in os.listdir(VIEWS_DIR) if f.endswith(".png"))

for fname in view_files:
    img = cv2.imread(os.path.join(VIEWS_DIR, fname), cv2.IMREAD_GRAYSCALE)

    # --- Step 1: detect the marker ---
    # corners: list of arrays, each shape (1, 4, 2) — the 4 pixel corners of one detected marker
    # ids:     which marker IDs were detected
    corners, ids, _ = detector.detectMarkers(img)

    if ids is None:
        print(f"[{fname}]  NO MARKER DETECTED")
        continue

    # corners[0] has shape (1, 4, 2) — squeeze to (4, 2)
    # These are the 2D pixel positions of the 4 marker corners in this image
    img_pts = corners[0].reshape(4, 2).astype(np.float64)

    # --- Step 2: solvePnP ---
    # Given:
    #   obj_pts  — where the corners are in 3D (we defined this, it's always the same)
    #   img_pts  — where the corners appear in the image (detected by ArUco)
    #   K        — how this camera projects 3D → 2D
    # Solve for: rvec, tvec — the pose that explains this observation
    success, rvec, tvec = cv2.solvePnP(obj_pts, img_pts, K, dist_coeffs)

    if not success:
        print(f"[{fname}]  solvePnP FAILED")
        continue

    # rvec is a Rodrigues rotation vector (3 numbers encoding axis and angle of rotation)
    # convert to degrees for readability
    rvec_deg = np.degrees(rvec).flatten()
    tvec_m   = tvec.flatten()

    # --- Step 3: compare with ground truth ---
    gt       = ground_truth["views"][fname.replace(".png", "")]
    gt_rvec  = np.array(gt["rvec_deg"], dtype=np.float64)
    gt_tvec  = np.array(gt["tvec_m"],   dtype=np.float64)

    rot_err  = np.abs(rvec_deg - gt_rvec)
    trans_err = np.abs(tvec_m  - gt_tvec) * 100   # convert to cm

    print(f"[{fname}]")
    print(f"  estimated  rvec: {rvec_deg.round(2)} deg   tvec: {tvec_m.round(4)} m")
    print(f"  ground truth   : {gt_rvec} deg   tvec: {gt_tvec} m")
    print(f"  error          : rot={rot_err.round(3)} deg   trans={trans_err.round(3)} cm")
    print()
