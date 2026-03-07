from __future__ import annotations

import os
import time

import cv2

try:
    import vlc
except ImportError:
    vlc = None

from src.vision.camera import set_fullscreen
from src.utils.resource_path import resource_path


def play_motivation_video_with_guard(
    *,
    video_path: str,
    window_name: str,
    cam,
    face_detector,
    is_face_in_center_roi_fn,
    restart_absent_s: float,
) -> bool:
    real_video_path = resource_path(video_path)

    if not os.path.exists(real_video_path):
        print(f"영상 파일이 없습니다: {real_video_path}")
        return False

    if vlc is None:
        print("python-vlc가 설치되지 않았습니다.")
        return False

    instance = vlc.Instance("--quiet")
    player = instance.media_player_new()
    media = instance.media_new(real_video_path)
    player.set_media(media)

    player.set_fullscreen(True)
    player.play()
    time.sleep(1.0)

    absent_start_t = None

    while True:
        ok, cam_frame = cam.read()
        if ok and cam_frame is not None:
            cam_frame = cv2.flip(cam_frame, 1)
            raw_fb = face_detector.detect(cam_frame)
            h, w = cam_frame.shape[:2]
            centered = is_face_in_center_roi_fn(raw_fb, w, h)

            if centered:
                absent_start_t = None
            else:
                if absent_start_t is None:
                    absent_start_t = time.time()
                elif time.time() - absent_start_t >= restart_absent_s:
                    player.stop()
                    time.sleep(0.4)
                    player.play()
                    time.sleep(1.0)
                    absent_start_t = None

        state = player.get_state()
        if state in (vlc.State.Ended, vlc.State.Stopped, vlc.State.Error):
            break

        time.sleep(0.03)

    player.stop()
    set_fullscreen(False)
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    return True