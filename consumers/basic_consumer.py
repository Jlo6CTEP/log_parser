from __future__ import annotations
from asyncio import Queue
from dataclasses import dataclass
from typing import List, Type

from events.base_event import BaseEvent
from logging_facility import logger


@dataclass
class SinkConsumer:
    queue: Queue[BaseEvent] = None
    events_to_respond: List[Type[BaseEvent]] = None

    def __init__(self, events_to_respond: List[Type[BaseEvent]]):
        self.queue = Queue()
        self.events_to_respond = events_to_respond

    async def process_event(self, item: BaseEvent) -> None:
        logger.debug(f"Sinked event {item}")

    async def _consume_from_queue(self):
        while True:
            item = await self.queue.get()
            await self.process_event(item)
            self.queue.task_done()



