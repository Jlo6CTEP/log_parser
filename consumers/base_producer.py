from __future__ import annotations

from dataclasses import dataclass

from consumers.basic_node import BasicNode
from events.base_event import BaseEvent
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from router.router import EventRouter


@dataclass
class BaseProducer(BasicNode):
    def __init__(self):
        super().__init__()

    async def produce(self) -> BaseEvent:
        pass

    async def _running_loop(self) -> None:
        while True:
            await self._router.route_event(await self.produce())
