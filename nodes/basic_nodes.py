from __future__ import annotations
from asyncio import Queue
from dataclasses import dataclass
from typing import Union, TYPE_CHECKING, List, Type

from events.base_event import BaseEvent
from logging_facility import logger

if TYPE_CHECKING:
    from router.router import EventRouter


@dataclass
class BaseNode:
    _router: EventRouter = None
    events_to_respond: List[Type[BaseEvent]] = None

    def __init__(self, *args, **kwargs):
        pass

    async def setup(self):
        """
        This will be run at the Node initialisation. Some file/stream opening,
        video capture etc can go here
        :return:
        """

    async def process(self, *args) -> Union[None, BaseEvent]:
        """
        Main function that produces / processes an event, or used as a listener
        of sorts
        :return:
        """
        pass

    async def _running_loop(self) -> None:
        """
        asynchronous loop that runs forever to process / produce events
        :return:
        """
        pass

    def _set_router(self, router: EventRouter):
        """
        Used to make this Node aware of a router
        (e.g. in case of a remote procedure call)
        :param router:
        :return:
        """
        self._router = router


@dataclass
class BaseConsumer(BaseNode):
    queue: Queue[BaseEvent] = None

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
                self._router.route_event(result)

    async def setup(self):
        self.queue = Queue()

    async def enqueue_event(self, event: BaseEvent):
        """
        Add an event to the event queue
        :param event:
        :return:
        """
        await self.queue.put(event)


@dataclass
class BaseProducer(BaseNode):
    def __init__(self):
        self.events_to_respond = []
        super().__init__()

    async def produce(self) -> BaseEvent:
        pass

    async def _running_loop(self) -> None:
        while True:
            self._router.route_event(await self.produce())

