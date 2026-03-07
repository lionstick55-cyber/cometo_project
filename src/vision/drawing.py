from __future__ import annotations

import cv2
import numpy as np

from src.vision.korean_text import put_korean_text


def draw_text_right(frame, lines):
    h, w = frame.shape[:2]
    y = 30

    for text in lines:
        (tw, th), _ = cv2.getTextSize(
            text,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            1,
        )
        x = w - tw - 20
        cv2.putText(
            frame,
            text,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 0, 0),
            1,
            cv2.LINE_AA,
        )
        y += 24


def draw_hands(frame, hand_results):
    for hand in hand_results:
        for x, y in hand.landmarks_px:
            cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

        if hand.landmarks_px:
            hx, hy = hand.landmarks_px[0]
            cv2.putText(
                frame,
                hand.handedness,
                (hx, hy - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )


def make_alert_screen(base_frame, alert_img, lines):
    h, w = base_frame.shape[:2]

    if alert_img is not None:
        screen = cv2.resize(alert_img, (w, h))
    else:
        screen = np.zeros((h, w, 3), dtype=np.uint8)
        screen[:] = (30, 30, 30)

    y = 40
    for text in lines:
        screen = put_korean_text(
            screen,
            text,
            (30, y),
            font_size=40,
            color=(255, 255, 255),
        )
        y += 60

    return screen