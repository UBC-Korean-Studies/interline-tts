import queue
import threading

import grpc

from .config import (
    AUDIO_MIME,
    DEFAULT_LANG,
    DEFAULT_SPEED,
    DEFAULT_STEPS,
    DEFAULT_VOICE,
    MAX_TEXT,
    SPEED_RANGE,
    STEPS_RANGE,
)
from .gen import tts_pb2, tts_pb2_grpc
from .pool import BadRequest, Job, Pool
from .text import split_text


class TtsService(tts_pb2_grpc.TtsServicer):
    def __init__(self, pool: Pool):
        self.pool = pool

    def Synthesize(self, request, context):
        text = request.text.strip()
        if not text:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "text is empty")
        if len(text) > MAX_TEXT:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT, f"text exceeds {MAX_TEXT} characters"
            )

        voice = request.voice or DEFAULT_VOICE
        lang = request.lang or DEFAULT_LANG
        speed = request.speed or DEFAULT_SPEED
        steps = request.total_steps or DEFAULT_STEPS
        if not SPEED_RANGE[0] <= speed <= SPEED_RANGE[1]:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT, f"speed must be in {SPEED_RANGE}"
            )
        if not STEPS_RANGE[0] <= steps <= STEPS_RANGE[1]:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                f"total_steps must be in {STEPS_RANGE}",
            )

        sentences = split_text(text)
        total = len(sentences)
        results: queue.Queue = queue.Queue()
        cancelled = threading.Event()
        context.add_callback(cancelled.set)

        jobs = [
            Job(i, s, voice, lang, speed, steps, results, cancelled)
            for i, s in enumerate(sentences)
        ]
        if not self.pool.submit(jobs):
            context.abort(grpc.StatusCode.RESOURCE_EXHAUSTED, "queue full, retry later")

        pending: dict = {}
        next_idx = 0
        while next_idx < total:
            try:
                idx, payload = results.get(timeout=0.5)
            except queue.Empty:
                if not context.is_active():
                    cancelled.set()
                    return
                continue
            if isinstance(payload, Exception):
                cancelled.set()
                code = (
                    grpc.StatusCode.INVALID_ARGUMENT
                    if isinstance(payload, BadRequest)
                    else grpc.StatusCode.INTERNAL
                )
                context.abort(code, str(payload))
            pending[idx] = payload

            while next_idx in pending:
                audio, dur = pending.pop(next_idx)
                yield tts_pb2.AudioChunk(
                    index=next_idx,
                    total=total,
                    text=sentences[next_idx],
                    audio=audio,
                    duration=dur,
                    mime_type=AUDIO_MIME,
                )
                next_idx += 1

    def GetStatus(self, request, context):
        return tts_pb2.StatusReply(
            workers=len(self.pool.threads),
            queued=self.pool.jobs.qsize(),
            active=self.pool.active,
        )
