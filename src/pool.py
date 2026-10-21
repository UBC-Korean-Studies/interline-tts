import itertools
import logging
import queue
import threading
from concurrent import futures

import numpy as np
from supertonic import TTS

from .config import MAX_QUEUE
from .encoding import encode_audio

log = logging.getLogger("interline-tts")


class BadRequest(Exception):
    """Client-side error (unknown voice, unsupported language, ...)."""


class Job:
    __slots__ = (
        "idx",
        "text",
        "voice",
        "lang",
        "speed",
        "steps",
        "results",
        "cancelled",
    )

    def __init__(self, idx, text, voice, lang, speed, steps, results, cancelled):
        self.idx, self.text, self.voice, self.lang = idx, text, voice, lang
        self.speed, self.steps = speed, steps
        self.results, self.cancelled = results, cancelled


class Pool:
    def __init__(self, n_workers: int):
        self.jobs: "queue.PriorityQueue[tuple]" = queue.PriorityQueue()
        self._seq = itertools.count()
        self.active = 0
        self._lock = threading.Lock()

        self.encoder = futures.ThreadPoolExecutor(
            max_workers=max(2, n_workers), thread_name_prefix="encode"
        )

        self.threads = []
        for i in range(n_workers):
            log.info("loading model for worker %d/%d", i + 1, n_workers)
            t = threading.Thread(
                target=self._run,
                args=(TTS(auto_download=True),),
                name=f"tts-worker-{i}",
                daemon=True,
            )
            self.threads.append(t)
        for t in self.threads:
            t.start()

    def _run(self, tts: TTS):
        styles: dict = {}
        while True:
            _, _, job = self.jobs.get()
            if job is None:
                return
            if job.cancelled.is_set():
                continue
            with self._lock:
                self.active += 1
            try:
                if job.voice not in styles:
                    try:
                        styles[job.voice] = tts.get_voice_style(voice_name=job.voice)
                    except Exception as e:
                        raise BadRequest(f"unknown voice {job.voice!r}: {e}") from e
                try:
                    samples, dur = tts.synthesize(
                        job.text,
                        voice_style=styles[job.voice],
                        lang=job.lang,
                        total_steps=job.steps,
                        speed=job.speed,
                    )
                except Exception as e:
                    raise BadRequest(
                        f"synthesis failed (lang={job.lang!r}): {e}"
                    ) from e
                duration = float(np.asarray(dur).reshape(-1)[0])
                self._encode(job, samples, tts.sample_rate, duration)
            except Exception as e:
                log.exception("job failed")
                job.results.put((job.idx, e))
            finally:
                with self._lock:
                    self.active -= 1

    def _encode(self, job: Job, samples, sr: int, duration: float):
        if job.cancelled.is_set():
            return
        fut = self.encoder.submit(encode_audio, samples, sr)

        def done(f):
            exc = f.exception()
            job.results.put(
                (job.idx, exc if exc is not None else (f.result(), duration))
            )

        fut.add_done_callback(done)

    def submit(self, jobs: list[Job]) -> bool:
        if self.jobs.qsize() + len(jobs) > MAX_QUEUE:
            return False
        for j in jobs:
            self.jobs.put((j.idx, next(self._seq), j))
        return True

    def stop(self):
        for _ in self.threads:
            self.jobs.put((float("inf"), next(self._seq), None))
        self.encoder.shutdown(wait=False, cancel_futures=True)
