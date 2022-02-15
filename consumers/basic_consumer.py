from __future__ import annotations
from asyncio import Queue
from dataclasses import dataclass
from typing import List, Type, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from router.router import EventRouter
from events.base_event import BaseEvent
from logging_facility import logger


@dataclass
class SinkConsumer:
    queue: Queue[BaseEvent] = None
    events_to_respond: List[Type[BaseEvent]] = None
    _router: EventRouter = None

    def __init__(self, events_to_respond: List[Type[BaseEvent]]):
        self.events_to_respond = events_to_respond

    async def process_event(self, item: BaseEvent) -> Union[None, BaseEvent]:
        logger.debug(f"Sinked event {item}")
        return None

    async def _process_events(self):
        while True:
            item = await self.queue.get()
            result = await self.process_event(item)
            self.queue.task_done()
            if result is not None:
                await self._router.route_event(result)

    async def _create_queue(self):
        self.queue = Queue()



