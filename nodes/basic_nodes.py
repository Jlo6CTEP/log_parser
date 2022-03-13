from __future__ import annotations
from asyncio import Queue
from dataclasses import dataclass
from typing import Union, TYPE_CHECKING, List, Type

from events.base_event import BaseEvent

if TYPE_CHECKING:
    from router.router import EventRouter


@dataclass
class BaseNode:
    _router: EventRouter = None
    events_to_respond: List[Type[BaseEvent]] = None

    def __init__(self):
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
