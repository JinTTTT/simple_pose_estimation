# Simple ArUco Pose Estimation

A minimal end-to-end example of 6DoF object pose estimation using ArUco markers and OpenCV's PnP solver. Built for learning purposes.

## What This Does

Given an RGB image containing an ArUco marker of known physical size, estimate the marker's **6DoF pose** (3D position + 3D orientation) relative to the camera.

```
RGB image  →  detect 4 marker corners (2D)  →  solvePnP  →  rotation + translation
```

Since no real camera or printed marker is needed, a simulator is included that generates synthetic views from known poses, which also serve as ground truth for evaluation.

## Pipeline

```
generate_marker.py   →   simulate_views.py   →   estimate_pose.py
   (create marker)       (render N views)        (detect + PnP + error)
```

## Requirements

```bash
pip install opencv-contrib-python numpy
```

## Usage

```bash
# 1. Generate the ArUco marker image
python3 generate_marker.py

# 2. Simulate camera views from known poses
python3 simulate_views.py

# 3. Run pose estimator and compare against ground truth
python3 estimate_pose.py
```

## Key Concepts

**ArUco marker** — a printed square with a black border and an inner binary cell pattern. The border gives 4 reliable corner points; the inner pattern encodes a unique ID and resolves rotational ambiguity.

**Camera matrix K** — describes the virtual camera (focal length, principal point). Must be consistent across all scripts.

**solvePnP** — given 4 known 3D corner positions and their detected 2D image positions, recovers the rotation vector `rvec` and translation vector `tvec` that explain the observation.

**Homography simulation** — because the marker is a flat plane, any perspective view of it can be synthesized exactly using a homography transform. This lets us generate ground truth data without a physical camera.

## Configuration

All tunable parameters are at the top of each script:

| Parameter | Default | Description |
|---|---|---|
| `MARKER_SIZE_M` | `0.1` | Physical side length of the marker in meters |
| `MARKER_ID` | `42` | ArUco marker ID (0–249 for DICT_6X6_250) |
| `IMG_W / IMG_H` | `640 / 480` | Simulated image resolution |
| `K` (focal length) | `600px` | Virtual camera focal length |

## Results

On the 5 simulated views, typical errors are:

- Rotation error: < 1 degree
- Translation error: < 1 cm

Error increases slightly with distance (fewer pixels → less precise corner detection).
