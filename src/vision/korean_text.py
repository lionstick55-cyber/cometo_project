from __future__ import annotations

import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from src.config import FONT_PATH


def put_korean_text(
    image_bgr: np.ndarray,
    text: str,
    position: tuple[int, int],
    font_size: int = 40,
    color: tuple[int, int, int] = (255, 255, 255),
) -> np.ndarray:
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(image_rgb)
    draw = ImageDraw.Draw(pil_img)

    if os.path.exists(FONT_PATH):
        font = ImageFont.truetype(FONT_PATH, font_size)
    else:
        font = ImageFont.load_default()

    draw.text(position, text, font=font, fill=color)
    out = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    return out