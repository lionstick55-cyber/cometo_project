import time


class FPSCounter:
    def __init__(self, alpha: float = 0.9):
        self.alpha = alpha
        self._last_t = None
        self._fps = 0.0

    def tick(self) -> float:
        now = time.time()
        if self._last_t is None:
            self._last_t = now
            return self._fps

        dt = now - self._last_t
        self._last_t = now
        if dt <= 0:
            return self._fps

        inst = 1.0 / dt
        # Exponential moving average for stable FPS display
        self._fps = self.alpha * self._fps + (1 - self.alpha) * inst
        return self._fps