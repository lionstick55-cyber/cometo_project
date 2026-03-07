from __future__ import annotations

from src.config import SWAY_WINDOW_S, SWAY_THRESHOLD_RATIO
from src.analysis.roi import get_center_roi


def is_face_touch(face_box, hand_results, frame_w: int, frame_h: int, margin: int = 20) -> bool:
    if face_box is None:
        return False

    x1 = max(0, face_box.x1 - margin)
    y1 = max(0, face_box.y1 - margin)
    x2 = min(frame_w - 1, face_box.x2 + margin)
    y2 = min(frame_h - 1, face_box.y2 + margin)

    fingertip_idx = [4, 8, 12, 16, 20]

    for hand in hand_results:
        for idx in fingertip_idx:
            if idx >= len(hand.landmarks_px):
                continue
            x, y = hand.landmarks_px[idx]
            if x1 <= x <= x2 and y1 <= y <= y2:
                return True

    return False


def update_sway_history(sway_history, now: float, face_box):
    if face_box is not None:
        cx = (face_box.x1 + face_box.x2) / 2.0
        sway_history.append((now, cx))

    while sway_history and (now - sway_history[0][0] > SWAY_WINDOW_S):
        sway_history.popleft()


def is_body_swaying(sway_history, frame_w: int) -> bool:
    if len(sway_history) < 5:
        return False

    xs = [x for _, x in sway_history]
    span = max(xs) - min(xs)
    return span >= frame_w * SWAY_THRESHOLD_RATIO


def compute_focus_score(face_present: bool, face_touch: bool, body_sway: bool, alert_active: bool) -> int:
    if alert_active:
        return 0

    score = 100

    if not face_present:
        score -= 60

    if face_touch:
        score -= 15

    if body_sway:
        score -= 20

    return max(0, min(100, score))


def is_any_hand_in_center_roi(hand_results, frame_w: int, frame_h: int) -> bool:
    rx1, ry1, rx2, ry2 = get_center_roi(frame_w, frame_h)

    for hand in hand_results:
        for x, y in hand.landmarks_px:
            if rx1 <= x <= rx2 and ry1 <= y <= ry2:
                return True

    return False