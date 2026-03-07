from __future__ import annotations

import time
from collections import deque

import cv2

from src.config import (
    WINDOW_NAME,
    ALERT_IMAGE_PATH,
    UNLOCK_PHRASE,
    ABSENT_MODE_THRESHOLD_S,
    TTS_START_THRESHOLD_S,
    FULLSCREEN_IMAGE_THRESHOLD_S,
    FACE_RETURN_REQUIRED_S,
    TTS_REPEAT_INTERVAL_S,
    FACE_TOUCH_MARGIN,
    GOOD_POSTURE_HOLD_S,
    MEAL_PAUSE_LIMIT,
    MOTIVATION_VIDEO_PATH,
    VIDEO_FACE_ABSENT_RESTART_S,
    UNLOCK_VIDEO_TRIGGER_COUNT,
    SESSION_LOG_PATH,
)
from src.detectors.face_detector import FaceDetector
from src.detectors.hands_detector import HandsDetector
from src.utils.fps import FPSCounter
from src.utils.session_logger import SessionLogger
from src.alerts.voice import VoiceAlert
from src.alerts.lock_screen import prompt_unlock
from src.analysis.roi import is_face_in_center_roi, draw_center_roi
from src.analysis.behavior import (
    is_face_touch,
    update_sway_history,
    is_body_swaying,
    compute_focus_score,
    is_any_hand_in_center_roi,
)
from src.vision.camera import open_camera, load_alert_image, set_fullscreen
from src.vision.drawing import draw_text_right, draw_hands, make_alert_screen
from src.vision.korean_text import put_korean_text
from src.vision.pause_ui import (
    make_pause_choice_screen,
    make_pause_reason_screen,
    is_clicked,
)
from src.vision.motivation_player import play_motivation_video_with_guard


mouse_state = {"x": -1, "y": -1, "clicked": False}


def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        mouse_state["x"] = x
        mouse_state["y"] = y
        mouse_state["clicked"] = True


def consume_click():
    if not mouse_state["clicked"]:
        return None
    x = mouse_state["x"]
    y = mouse_state["y"]
    mouse_state["clicked"] = False
    return x, y


def play_motivation(cam, face_detector, session_logger: SessionLogger):
    ok = play_motivation_video_with_guard(
        video_path=MOTIVATION_VIDEO_PATH,
        window_name=WINDOW_NAME,
        cam=cam,
        face_detector=face_detector,
        is_face_in_center_roi_fn=is_face_in_center_roi,
        restart_absent_s=VIDEO_FACE_ABSENT_RESTART_S,
    )
    if ok:
        session_logger.add_video_play()


def run_pause_menu(frame, session_logger: SessionLogger):
    cv2.setMouseCallback(WINDOW_NAME, on_mouse)

    while True:
        choice_screen, choice_buttons = make_pause_choice_screen(frame)
        cv2.imshow(WINDOW_NAME, choice_screen)

        click = consume_click()
        if click:
            x, y = click
            print(f"[pause menu click] x={x}, y={y}")

            clicked_label = None
            for btn in choice_buttons:
                if is_clicked(btn, x, y):
                    clicked_label = btn.label
                    print(f"[pause menu] clicked: {clicked_label}")
                    break

            if clicked_label == "종료":
                return "exit", None
            if clicked_label == "정지":
                break

        key = cv2.waitKey(30) & 0xFF
        if key == ord("q"):
            print("[pause menu] q pressed again -> resume")
            return "resume", None

    selected_reason = None

    while True:
        meal_count = session_logger.get_reason_count("밥")
        reason_screen, reason_buttons, bottom_buttons = make_pause_reason_screen(
            frame=frame,
            meal_count=meal_count,
            meal_limit=MEAL_PAUSE_LIMIT,
            selected_reason=selected_reason,
        )
        cv2.imshow(WINDOW_NAME, reason_screen)

        click = consume_click()
        if click:
            x, y = click
            print(f"[reason menu click] x={x}, y={y}")

            for btn in reason_buttons:
                if is_clicked(btn, x, y):
                    if btn.label.startswith("밥"):
                        selected_reason = "밥"
                    else:
                        selected_reason = btn.label
                    print(f"[reason menu] selected_reason = {selected_reason}")
                    break

            for btn in bottom_buttons:
                if is_clicked(btn, x, y):
                    print(f"[reason menu] bottom button = {btn.label}")

                    if selected_reason:
                        session_logger.add_pause_reason(selected_reason)

                    if btn.label == "종료":
                        return "exit", selected_reason
                    if btn.label == "재시작":
                        return "resume", selected_reason

        key = cv2.waitKey(30) & 0xFF
        if key == ord("q"):
            print("[reason menu] q pressed again -> resume")
            return "resume", selected_reason


def main():
    cap = open_camera()
    if cap is None:
        print("Cannot open camera")
        return

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(WINDOW_NAME, on_mouse)

    face = FaceDetector(min_detection_confidence=0.6)
    hands = HandsDetector(
        max_num_hands=2,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.5,
    )
    fps_counter = FPSCounter(alpha=0.9)
    voice = VoiceAlert()
    session_logger = SessionLogger(save_path=SESSION_LOG_PATH)

    alert_img = load_alert_image(ALERT_IMAGE_PATH)

    last_face_seen_t = time.time()
    sway_history = deque()

    alert_active = False
    alert_started_t = None
    return_face_start_t = None
    fullscreen_on = False

    posture_hold_start_t = None
    show_posture_text = False

    unlock_success_since_video = 0

    try:
        while True:
            ok, frame = cap.read()
            if not ok or frame is None:
                print("Failed to read frame")
                break

            frame = cv2.flip(frame, 1)

            now = time.time()
            fps = fps_counter.tick()

            raw_fb = face.detect(frame)
            hand_results = hands.detect(frame)

            frame_h, frame_w = frame.shape[:2]
            face_in_roi = is_face_in_center_roi(raw_fb, frame_w, frame_h)
            fb = raw_fb if face_in_roi else None

            face_present = fb is not None
            hand_count = len(hand_results)

            if face_present:
                last_face_seen_t = now

            absent_secs = now - last_face_seen_t
            mode = "ABSENT" if absent_secs >= ABSENT_MODE_THRESHOLD_S else "PRESENT"

            update_sway_history(sway_history, now, fb)
            body_sway = is_body_swaying(sway_history, frame_w)
            face_touch = is_face_touch(fb, hand_results, frame_w, frame_h, FACE_TOUCH_MARGIN)

            hand_in_roi = is_any_hand_in_center_roi(hand_results, frame_w, frame_h)
            if face_present and hand_in_roi:
                if posture_hold_start_t is None:
                    posture_hold_start_t = now
                hold_secs = now - posture_hold_start_t
                show_posture_text = hold_secs >= GOOD_POSTURE_HOLD_S
            else:
                posture_hold_start_t = None
                show_posture_text = False

            if not alert_active and absent_secs >= TTS_START_THRESHOLD_S:
                alert_active = True
                alert_started_t = now
                return_face_start_t = None

            if alert_active:
                alert_elapsed = now - alert_started_t if alert_started_t is not None else 0.0

                if face_present:
                    if return_face_start_t is None:
                        return_face_start_t = now

                    face_return_secs = now - return_face_start_t

                    if face_return_secs >= FACE_RETURN_REQUIRED_S:
                        ok_unlock = prompt_unlock(UNLOCK_PHRASE)
                        if ok_unlock:
                            session_logger.add_unlock_success()
                            unlock_success_since_video += 1

                            if unlock_success_since_video >= UNLOCK_VIDEO_TRIGGER_COUNT:
                                play_motivation(cap, face, session_logger)
                                unlock_success_since_video = 0

                            alert_active = False
                            alert_started_t = None
                            return_face_start_t = None
                            last_face_seen_t = now
                            mode = "PRESENT"
                else:
                    return_face_start_t = None
                    voice.speak_focus(min_interval=TTS_REPEAT_INTERVAL_S)

                if alert_elapsed >= FULLSCREEN_IMAGE_THRESHOLD_S:
                    if not fullscreen_on:
                        set_fullscreen(True)
                        fullscreen_on = True

                    if face_present and return_face_start_t is not None:
                        face_return_secs = now - return_face_start_t
                    else:
                        face_return_secs = 0.0

                    alert_lines = [
                        "집중하세요",
                        f"얼굴 복귀 유지 시간: {face_return_secs:.1f}s / {FACE_RETURN_REQUIRED_S:.0f}s",
                        f'입력 문구: "{UNLOCK_PHRASE}"',
                    ]

                    screen = make_alert_screen(frame, alert_img, alert_lines)
                    cv2.imshow(WINDOW_NAME, screen)

                    key = cv2.waitKey(1) & 0xFF
                    if key == ord("q"):
                        action, reason = run_pause_menu(frame, session_logger)
                        if action == "exit":
                            break
                        if reason == "솔직히 집중하기 힘듬":
                            play_motivation(cap, face, session_logger)
                    continue
                else:
                    if fullscreen_on:
                        set_fullscreen(False)
                        fullscreen_on = False
            else:
                if fullscreen_on:
                    set_fullscreen(False)
                    fullscreen_on = False

            if raw_fb is not None:
                cv2.rectangle(
                    frame,
                    (raw_fb.x1, raw_fb.y1),
                    (raw_fb.x2, raw_fb.y2),
                    (180, 180, 180),
                    1,
                )

            if fb is not None:
                cv2.rectangle(
                    frame,
                    (fb.x1, fb.y1),
                    (fb.x2, fb.y2),
                    (255, 255, 255),
                    2,
                )

            draw_center_roi(frame)
            draw_hands(frame, hand_results)

            focus_score = compute_focus_score(
                face_present=face_present,
                face_touch=face_touch,
                body_sway=body_sway,
                alert_active=alert_active,
            )

            lines = [
                f"Mode: {mode}",
                f"Focus: {focus_score}",
                f"FPS: {fps:.1f}",
                f"Absent: {absent_secs:.1f}s",
                f"Hands: {hand_count}",
                f"FaceTouch: {'YES' if face_touch else 'NO'}",
                f"Sway: {'YES' if body_sway else 'NO'}",
                f"CenterFace: {'YES' if face_present else 'NO'}",
                f"Alert: {'ON' if alert_active else 'OFF'}",
                f"UnlockCount: {unlock_success_since_video}/{UNLOCK_VIDEO_TRIGGER_COUNT}",
            ]

            draw_text_right(frame, lines)

            if show_posture_text:
                voice.speak_posture(min_interval=3.0)
                frame = put_korean_text(
                    frame,
                    "바른자세 합시다",
                    (25, 30),
                    font_size=34,
                    color=(0, 255, 255),
                )

            cv2.imshow(WINDOW_NAME, frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                action, reason = run_pause_menu(frame, session_logger)
                if action == "exit":
                    break
                if reason == "솔직히 집중하기 힘듬":
                    play_motivation(cap, face, session_logger)

    finally:
        session_logger.save()
        print(f"{SESSION_LOG_PATH} 저장 완료")
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()