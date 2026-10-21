"""gRPC server wiring and lifecycle."""

import logging
import shutil
import signal
import threading
from concurrent import futures

import grpc

from .config import ADDR, AUDIO_BITRATE, DEFAULT_LANG, DEFAULT_VOICE, N_WORKERS
from .gen import tts_pb2_grpc
from .pool import Pool
from .service import TtsService

log = logging.getLogger("interline-tts")


def serve():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg not found on PATH (add pkgs.ffmpeg to shell.nix)")
    log.info(
        "starting with %d worker(s), default voice=%s lang=%s, opus %s",
        N_WORKERS,
        DEFAULT_VOICE,
        DEFAULT_LANG,
        AUDIO_BITRATE,
    )
    pool = Pool(N_WORKERS)
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=64),
        maximum_concurrent_rpcs=64,
        options=[("grpc.max_send_message_length", 32 * 1024 * 1024)],
    )
    tts_pb2_grpc.add_TtsServicer_to_server(TtsService(pool), server)
    server.add_insecure_port(ADDR)
    server.start()
    log.info("listening on %s", ADDR)

    stop = threading.Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: stop.set())
    stop.wait()
    log.info("shutting down")
    server.stop(grace=5).wait()
    pool.stop()
