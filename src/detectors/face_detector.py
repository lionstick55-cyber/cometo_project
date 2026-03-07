from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import cv2
import mediapipe as mp


@dataclass(frozen=True)
class FaceBox:
    x1: int
    y1: int
    x2: int
    y2: int

    def clamp(self, w: int, h: int) -> "FaceBox":
        x1 = max(0, min(self.x1, w - 1))
        y1 = max(0, min(self.y1, h - 1))
        x2 = max(0, min(self.x2, w - 1))
        y2 = max(0, min(self.y2, h - 1))
        if x2 < x1:
            x1, x2 = x2, x1
        if y2 < y1:
            y1, y2 = y2, y1
        return FaceBox(x1, y1, x2, y2)


class FaceDetector:
    """
    MediaPipe Face Detection wrapper.
    가장 큰 얼굴 1개를 반환.
    """

    def __init__(self, min_detection_confidence: float = 0.6):
        self._detector = mp.solutions.face_detection.FaceDetection(
            model_selection=0,
            min_detection_confidence=min_detection_confidence,
        )

    def detect(self, bgr_frame) -> Optional[FaceBox]:
        h, w = bgr_frame.shape[:2]
        rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        result = self._detector.process(rgb)

        if not result.detections:
            return None

        best_box = None
        best_area = -1

        for det in result.detections:
            box = det.location_data.relative_bounding_box
            x1 = int(box.xmin * w)
            y1 = int(box.ymin * h)
            x2 = int((box.xmin + box.width) * w)
            y2 = int((box.ymin + box.height) * h)

            fb = FaceBox(x1, y1, x2, y2).clamp(w, h)
            area = (fb.x2 - fb.x1) * (fb.y2 - fb.y1)

            if area > best_area:
                best_area = area
                best_box = fb

        return best_box