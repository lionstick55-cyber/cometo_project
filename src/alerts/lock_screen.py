from __future__ import annotations

import tkinter as tk
from tkinter import simpledialog


def prompt_unlock(expected_text: str) -> bool:
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    try:
        while True:
            value = simpledialog.askstring(
                "잠금 해제",
                f'"{expected_text}" 를 정확히 입력해야 다시 사용할 수 있습니다.',
                parent=root,
            )
            if value == expected_text:
                return True
    finally:
        root.destroy()