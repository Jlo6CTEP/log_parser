import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import List, Type, Union

from consumers.basic_consumer import SinkConsumer
from events.base_event import BaseEvent
from events.ping import PingEvent, PongEvent


@dataclass
class PingEventConsumer(SinkConsumer):

    def __init__(self, events_to_respond: List[Type[BaseEvent]]):
        super().__init__(events_to_respond)

    async def process_event(self, item: PingEvent) -> Union[None, BaseEvent]:
        print(f"got pinged, {item}")
        await asyncio.sleep(2)
        return PongEvent(datetime.now().time(), "pong")
