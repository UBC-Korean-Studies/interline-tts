import os

ADDR = os.getenv("TTS_ADDR", "127.0.0.1:50051")
DEFAULT_VOICE = os.getenv("TTS_DEFAULT_VOICE", "M4")
DEFAULT_LANG = os.getenv("TTS_DEFAULT_LANG", "ko")
DEFAULT_SPEED = 1
DEFAULT_STEPS = 8
SPEED_RANGE = (0.7, 2.0)
STEPS_RANGE = (5, 12)
N_WORKERS = int(os.getenv("TTS_WORKERS", max(1, (os.cpu_count() or 4) // 4)))
MAX_QUEUE = int(os.getenv("TTS_MAX_QUEUE", "256"))
MAX_TEXT = int(os.getenv("TTS_MAX_TEXT", "20000"))
MAX_SENTENCE = 200

AUDIO_BITRATE = os.getenv("TTS_BITRATE", "32k")
AUDIO_MIME = "audio/ogg; codecs=opus"
