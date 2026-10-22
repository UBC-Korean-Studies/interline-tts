from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class SynthesizeRequest(_message.Message):
    __slots__ = ("text", "lang", "voice", "speed", "total_steps")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    LANG_FIELD_NUMBER: _ClassVar[int]
    VOICE_FIELD_NUMBER: _ClassVar[int]
    SPEED_FIELD_NUMBER: _ClassVar[int]
    TOTAL_STEPS_FIELD_NUMBER: _ClassVar[int]
    text: str
    lang: str
    voice: str
    speed: float
    total_steps: int
    def __init__(
        self,
        text: _Optional[str] = ...,
        lang: _Optional[str] = ...,
        voice: _Optional[str] = ...,
        speed: _Optional[float] = ...,
        total_steps: _Optional[int] = ...,
    ) -> None: ...

class AudioChunk(_message.Message):
    __slots__ = ("index", "total", "text", "audio", "duration", "mime_type")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    AUDIO_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    MIME_TYPE_FIELD_NUMBER: _ClassVar[int]
    index: int
    total: int
    text: str
    audio: bytes
    duration: float
    mime_type: str
    def __init__(
        self,
        index: _Optional[int] = ...,
        total: _Optional[int] = ...,
        text: _Optional[str] = ...,
        audio: _Optional[bytes] = ...,
        duration: _Optional[float] = ...,
        mime_type: _Optional[str] = ...,
    ) -> None: ...

class StatusRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StatusReply(_message.Message):
    __slots__ = ("workers", "queued", "active")
    WORKERS_FIELD_NUMBER: _ClassVar[int]
    QUEUED_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    workers: int
    queued: int
    active: int
    def __init__(
        self,
        workers: _Optional[int] = ...,
        queued: _Optional[int] = ...,
        active: _Optional[int] = ...,
    ) -> None: ...
