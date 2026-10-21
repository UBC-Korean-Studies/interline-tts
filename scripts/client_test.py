"""Manual client: synthesize a Korean passage, save each chunk, report timing."""

import sys
import time
from pathlib import Path

import grpc

from src.gen import tts_pb2, tts_pb2_grpc

TEXT = (
    "지난 겨울, 춘천 근처에 있는 청평사에 놀러 갔을 때에 있었던 일이다. "
    "평일인데다가 소양댐에서 첫배를 탔기 때문에 청평사로 가는 사람이 나 말고는 아무도 없었다. "
    "그런데 5분쯤 올라가다 보니 앞에 한 남자가 걸어가고 있는 것이 보였다. "
    "나는 전날 그 근처에서 묵은 여행객일 거라고 생각했다. "
    "그 사람도 내가 따라오고 있는 것을 느꼈는지 뒤를 돌아다보았다. "
    "그리고는 내가 자기보다 앞에 갈까 봐 걸음을 재촉하는 것 이었다. "
    "호기심이 생겨서 내가 열심히 따라갔더니 그 사람은 더 빨리 걷는 것이었다. "
    "나는 도대체 그 사람이 왜 그러는지 알 수가 없었다. "
    "그런데 잠시 후 아직 문을 열지 않은 청평사 매표소가 나타났을 때 의문이 풀렸다. "
    "그 사람은 거기서 표를 파는 사람이었다."
)

OUT_DIR = Path("out")


def main(addr: str = "127.0.0.1:50051") -> None:
    OUT_DIR.mkdir(exist_ok=True)
    audio_total = 0.0
    first_chunk_at = None

    with grpc.insecure_channel(addr) as channel:
        stub = tts_pb2_grpc.TtsStub(channel)
        t0 = time.perf_counter()
        for chunk in stub.Synthesize(tts_pb2.SynthesizeRequest(text=TEXT)):
            now = time.perf_counter() - t0
            if first_chunk_at is None:
                first_chunk_at = now
            audio_total += chunk.duration

            (OUT_DIR / f"out_{chunk.index}.opus").write_bytes(chunk.audio)
            print(
                f"{chunk.index + 1}/{chunk.total} "
                f"audio={chunk.duration:.2f}s arrived@{now:.2f}s  {chunk.text}"
            )
        total = time.perf_counter() - t0

    if first_chunk_at is not None and audio_total > 0:
        print()
        print(f"time to first chunk: {first_chunk_at:.2f}s")
        print(f"total wall time:     {total:.2f}s")
        print(f"total audio:         {audio_total:.1f}s")
        print(
            f"real-time factor:    {total / audio_total:.2f}  (below 1.0 = faster than playback)"
        )


if __name__ == "__main__":
    main(*sys.argv[1:2])
