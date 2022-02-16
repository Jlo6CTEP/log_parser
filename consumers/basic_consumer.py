from __future__ import annotations
from asyncio import Queue
from dataclasses import dataclass
from typing import List, Type, TYPE_CHECKING, Union

from consumers.basic_node import BasicNode

if TYPE_CHECKING:
    from events.base_event import BaseEvent
from logging_facility import logger


@dataclass
class SinkConsumer(BasicNode):
    queue: Queue[BaseEvent] = None
    events_to_respond: List[Type[BaseEvent]] = None

    def __init__(self, events_to_respond: List[Type[BaseEvent]]):
        super().__init__()
        self.events_to_respond = events_to_respond

    async def process(self, item: BaseEvent) -> Union[None, BaseEvent]:
        logger.debug(f"Sinked event {item}")
        return None

    async def _running_loop(self) -> None:
        while True:
            item = await self.queue.get()
            result = await self.process(item)
            self.queue.task_done()
            if result is not None:
                await self._router.route_event(result)

    async def _create_queue(self):
        """
        At the initialisation, create an event Queue to communicate with router
        :return:
        """
        self.queue = Queue()

    async def enqueue_event(self, event: BaseEvent):
        """
        Add an event to the event queue
        :param event:
        :return:
        """
        await self.queue.put(event)






