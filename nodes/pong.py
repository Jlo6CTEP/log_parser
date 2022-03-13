import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import List, Type, Union

from consumers.basic_consumer import BaseConsumer
from events.base_event import BaseEvent
from events.ping import PingEvent, PongEvent


@dataclass
class PongEventConsumer(BaseConsumer):

    def __init__(self, events_to_respond: List[Type[BaseEvent]]):
        super().__init__(events_to_respond)

    async def process(self, item: PongEvent) -> Union[None, BaseEvent]:
        print(f"got ponged, {item}")
        await asyncio.sleep(2)
        return PingEvent(datetime.now().time(), "ping")