from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import cv2
import mediapipe as mp


@dataclass
class HandResult:
    landmarks_px: List[Tuple[int, int]]
    handedness: str  # "Left" or "Right"


class HandsDetector:
    def __init__(
        self,
        max_num_hands: int = 2,
        min_detection_confidence: float = 0.6,
        min_tracking_confidence: float = 0.5,
    ):
        self._hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self._drawer = mp.solutions.drawing_utils
        self._styles = mp.solutions.drawing_styles
        self._hands_module = mp.solutions.hands

    def detect(self, bgr_frame) -> List[HandResult]:
        h, w = bgr_frame.shape[:2]
        rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        result = self._hands.process(rgb)

        outputs: List[HandResult] = []

        if result.multi_hand_landmarks and result.multi_handedness:
            for hand_landmarks, handedness in zip(
                result.multi_hand_landmarks,
                result.multi_handedness
            ):
                pts = []
                for lm in hand_landmarks.landmark:
                    x = int(lm.x * w)
                    y = int(lm.y * h)
                    pts.append((x, y))

                label = handedness.classification[0].label
                outputs.append(HandResult(landmarks_px=pts, handedness=label))

        return outputs

    def draw(self, frame, hand_results_raw):
        if not hand_results_raw.multi_hand_landmarks:
            return

        for hand_landmarks in hand_results_raw.multi_hand_landmarks:
            self._drawer.draw_landmarks(
                frame,
                hand_landmarks,
                self._hands_module.HAND_CONNECTIONS,
                self._styles.get_default_hand_landmarks_style(),
                self._styles.get_default_hand_connections_style(),
            )