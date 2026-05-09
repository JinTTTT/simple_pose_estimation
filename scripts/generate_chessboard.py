from pathlib import Path


# OpenCV chessboard calibration counts inner corners, not squares.
# A 9x6 inner-corner board has 10x7 physical squares.
INNER_CORNERS_X = 9
INNER_CORNERS_Y = 6
SQUARE_SIZE_MM = 25

SQUARES_X = INNER_CORNERS_X + 1
SQUARES_Y = INNER_CORNERS_Y + 1

PAGE_W_MM = 297
PAGE_H_MM = 210
BOARD_W_MM = SQUARES_X * SQUARE_SIZE_MM
BOARD_H_MM = SQUARES_Y * SQUARE_SIZE_MM
OFFSET_X_MM = (PAGE_W_MM - BOARD_W_MM) / 2
OFFSET_Y_MM = (PAGE_H_MM - BOARD_H_MM) / 2

ROOT_DIR = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT_DIR / "images" / "targets" / "chessboard_9x6_25mm.svg"


def main():
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{PAGE_W_MM}mm" '
        f'height="{PAGE_H_MM}mm" viewBox="0 0 {PAGE_W_MM} {PAGE_H_MM}">',
        '<rect width="100%" height="100%" fill="white"/>',
    ]

    for y in range(SQUARES_Y):
        for x in range(SQUARES_X):
            if (x + y) % 2 == 0:
                parts.append(
                    f'<rect x="{OFFSET_X_MM + x * SQUARE_SIZE_MM}" '
                    f'y="{OFFSET_Y_MM + y * SQUARE_SIZE_MM}" '
                    f'width="{SQUARE_SIZE_MM}" height="{SQUARE_SIZE_MM}" '
                    'fill="black"/>'
                )

    parts.extend(
        [
            f'<rect x="{OFFSET_X_MM}" y="{OFFSET_Y_MM}" width="{BOARD_W_MM}" '
            f'height="{BOARD_H_MM}" fill="none" stroke="black" stroke-width="0.2"/>',
            "</svg>",
        ]
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(parts), encoding="utf-8")
    print(f"Saved {OUT_PATH}")
    print(f"Inner corners: {INNER_CORNERS_X} x {INNER_CORNERS_Y}")
    print(f"Square size: {SQUARE_SIZE_MM} mm")
    print(f"Board size: {BOARD_W_MM} x {BOARD_H_MM} mm")
    print("Print on A4 landscape at 100% scale / actual size.")


if __name__ == "__main__":
    main()
