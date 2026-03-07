import threading
import time

import pyttsx3


class VoiceAlert:
    def __init__(self):
        self._lock = threading.Lock()
        self._speaking = False
        self._last_t = 0.0

    def speak(self, text: str, min_interval: float = 0.5):
        now = time.time()

        with self._lock:
            if self._speaking:
                return
            if now - self._last_t < min_interval:
                return

            self._speaking = True
            self._last_t = now

        thread = threading.Thread(target=self._worker, args=(text,), daemon=True)
        thread.start()

    def speak_focus(self, min_interval: float = 0.5):
        self.speak("집중하세요", min_interval=min_interval)

    def speak_posture(self, min_interval: float = 3.0):
        self.speak("바른자세 하세요", min_interval=min_interval)

    def _worker(self, text: str):
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty("voices")

            if voices:
                engine.setProperty("voice", voices[0].id)

            engine.setProperty("rate", 170)
            engine.setProperty("volume", 1.0)

            engine.say(text)
            engine.runAndWait()
            engine.stop()
        finally:
            with self._lock:
                self._speaking = False