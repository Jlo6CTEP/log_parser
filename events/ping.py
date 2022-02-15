from dataclasses import dataclass

from events.base_event import BaseEvent


@dataclass
class PingEvent(BaseEvent):
    message: str = "ping"


@dataclass
class PongEvent(BaseEvent):
    message: str = "pong"
