import subprocess

import numpy as np

from .config import AUDIO_BITRATE


def encode_audio(samples, sample_rate: int) -> bytes:
    """Synthesized float samples -> self-contained Ogg/Opus bytes."""
    pcm = (
        (np.clip(np.asarray(samples, dtype=np.float32).reshape(-1), -1.0, 1.0) * 32767)
        .astype(np.int16)
        .tobytes()
    )
    proc = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "s16le",
            "-ar",
            str(sample_rate),
            "-ac",
            "1",
            "-i",
            "pipe:0",
            "-ar",
            "48000",
            "-c:a",
            "libopus",
            "-b:a",
            AUDIO_BITRATE,
            "-application",
            "voip",
            "-f",
            "ogg",
            "pipe:1",
        ],
        input=pcm,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {proc.stderr.decode(errors='replace')}")
    return proc.stdout
