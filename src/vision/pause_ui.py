from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from src.vision.korean_text import put_korean_text


@dataclass
class Button:
    label: str
    x1: int
    y1: int
    x2: int
    y2: int
    enabled: bool = True


def is_clicked(button: Button, x: int, y: int) -> bool:
    return button.enabled and button.x1 <= x <= button.x2 and button.y1 <= y <= button.y2


def draw_button(img, button: Button):
    fill = (60, 110, 170) if button.enabled else (70, 70, 70)

    cv2.rectangle(img, (button.x1, button.y1), (button.x2, button.y2), fill, -1)
    cv2.rectangle(img, (button.x1, button.y1), (button.x2, button.y2), (255, 255, 255), 2)

    img = put_korean_text(
        img,
        button.label,
        (button.x1 + 18, button.y1 + 14),
        font_size=24,
        color=(255, 255, 255),
    )
    return img


def make_pause_choice_screen(frame):
    h, w = frame.shape[:2]
    screen = frame.copy()

    overlay = np.zeros_like(screen)
    overlay[:] = (20, 20, 20)
    screen = cv2.addWeighted(screen, 0.3, overlay, 0.7, 0)

    screen = put_korean_text(screen, "프로그램을 종료할까요, 정지할까요?", (45, 40), font_size=34)

    btn_w = 150
    btn_h = 60
    y = h // 2 - 30

    exit_btn = Button("종료", w // 2 - 220, y, w // 2 - 70, y + btn_h)
    pause_btn = Button("정지", w // 2 + 70, y, w // 2 + 220, y + btn_h)

    buttons = [exit_btn, pause_btn]

    for btn in buttons:
        screen = draw_button(screen, btn)
        

    return screen, buttons


def make_pause_reason_screen(frame, meal_count: int, meal_limit: int, selected_reason: str | None):
    h, w = frame.shape[:2]
    screen = np.zeros_like(frame)
    screen[:] = (25, 25, 25)

    screen = put_korean_text(screen, "정지 사유를 선택하세요", (45, 35), font_size=34)

    btn_w = 220
    btn_h = 54
    left_x = 60
    right_x = w - btn_w - 60
    top_y = 100
    row_gap = 28

    labels = [
        ("담타", True),
        ("화장실", True),
        (f"밥 ({meal_count}/{meal_limit})", meal_count < meal_limit),
        ("솔직히 집중하기 힘듬", True),
    ]

    reason_buttons = []
    for i, (label, enabled) in enumerate(labels):
        col_x = left_x if i % 2 == 0 else right_x
        row_y = top_y + (i // 2) * (btn_h + row_gap)
        btn = Button(label, col_x, row_y, col_x + btn_w, row_y + btn_h, enabled=enabled)
        reason_buttons.append(btn)
        screen = draw_button(screen, btn)

    bottom_buttons = []

    if selected_reason is not None:
        screen = put_korean_text(
            screen,
            f"선택된 사유: {selected_reason}",
            (45, h - 145),
            font_size=28,
            color=(255, 255, 255),
        )

        bottom_y = h - 82
        small_w = 140
        small_h = 52

        if selected_reason == "솔직히 집중하기 힘듬":
            bottom_buttons.append(Button("재시작", w - small_w - 50, bottom_y, w - 50, bottom_y + small_h))
        else:
            bottom_buttons.append(Button("종료", 50, bottom_y, 50 + small_w, bottom_y + small_h))
            bottom_buttons.append(Button("재시작", w - small_w - 50, bottom_y, w - 50, bottom_y + small_h))

    for btn in bottom_buttons:
        screen = draw_button(screen, btn)

    return screen, reason_buttons, bottom_buttons