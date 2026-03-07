from __future__ import annotations

import json
import time


class SessionLogger:
    def __init__(self, save_path: str):
        self.save_path = save_path
        self.started_at = time.time()

        self.pause_total_count = 0
        self.pause_reason_counts = {
            "담타": 0,
            "화장실": 0,
            "밥": 0,
            "솔직히 집중하기 힘듬": 0,
        }

        self.unlock_success_count = 0
        self.motivation_video_play_count = 0

    def add_pause_reason(self, reason: str) -> None:
        if reason not in self.pause_reason_counts:
            return
        self.pause_total_count += 1
        self.pause_reason_counts[reason] += 1

    def get_reason_count(self, reason: str) -> int:
        return self.pause_reason_counts.get(reason, 0)

    def add_unlock_success(self) -> None:
        self.unlock_success_count += 1

    def add_video_play(self) -> None:
        self.motivation_video_play_count += 1

    def save(self) -> None:
        total_runtime_s = round(time.time() - self.started_at, 1)

        data = {
            "total_runtime_s": total_runtime_s,
            "pause_total_count": self.pause_total_count,
            "pause_reason_counts": self.pause_reason_counts,
            "unlock_success_count": self.unlock_success_count,
            "motivation_video_play_count": self.motivation_video_play_count,
            "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        with open(self.save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)