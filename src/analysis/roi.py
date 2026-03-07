from __future__ import annotations

import cv2

from src.config import ROI_WIDTH_RATIO, ROI_HEIGHT_RATIO


def get_center_roi(frame_w: int, frame_h: int):
    roi_w = int(frame_w * ROI_WIDTH_RATIO)
    roi_h = int(frame_h * ROI_HEIGHT_RATIO)

    x1 = (frame_w - roi_w) // 2
    y1 = (frame_h - roi_h) // 2
    x2 = x1 + roi_w
    y2 = y1 + roi_h
    return x1, y1, x2, y2


def is_face_in_center_roi(face_box, frame_w: int, frame_h: int) -> bool:
    if face_box is None:
        return False

    rx1, ry1, rx2, ry2 = get_center_roi(frame_w, frame_h)

    cx = (face_box.x1 + face_box.x2) / 2.0
    cy = (face_box.y1 + face_box.y2) / 2.0

    return rx1 <= cx <= rx2 and ry1 <= cy <= ry2


def draw_center_roi(frame):
    h, w = frame.shape[:2]
    x1, y1, x2, y2 = get_center_roi(w, h)
    cv2.rectangle(frame, (x1, y1), (x2, y2), (180, 180, 180), 1)