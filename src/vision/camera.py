from __future__ import annotations

import os

import cv2

from src.config import WINDOW_NAME
from src.utils.resource_path import resource_path


def open_camera(max_index: int = 4):
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]

    for backend in backends:
        for idx in range(max_index):
            cap = cv2.VideoCapture(idx, backend)

            if not cap.isOpened():
                cap.release()
                continue

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)

            ok, frame = False, None
            for _ in range(10):
                ok, frame = cap.read()
                if ok and frame is not None:
                    break

            if ok and frame is not None:
                print(f"Camera opened: index={idx}, backend={backend}")
                return cap

            cap.release()

    return None


def load_alert_image(path: str):
    real_path = resource_path(path)
    if os.path.exists(real_path):
        return cv2.imread(real_path)
    return None


def set_fullscreen(enabled: bool):
    flag = cv2.WINDOW_FULLSCREEN if enabled else cv2.WINDOW_NORMAL
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, flag)