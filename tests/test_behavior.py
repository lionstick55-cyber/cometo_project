from collections import deque

from src.analysis.behavior import compute_focus_score, is_body_swaying


def test_compute_focus_score_normal():
    score = compute_focus_score(
        face_present=True,
        face_touch=False,
        body_sway=False,
        alert_active=False,
    )
    assert score == 100


def test_compute_focus_score_alert():
    score = compute_focus_score(
        face_present=True,
        face_touch=False,
        body_sway=False,
        alert_active=True,
    )
    assert score == 0


def test_is_body_swaying_true():
    history = deque([
        (0.0, 100),
        (0.5, 110),
        (1.0, 140),
        (1.5, 170),
        (2.0, 200),
    ])
    assert is_body_swaying(history, frame_w=640) is True