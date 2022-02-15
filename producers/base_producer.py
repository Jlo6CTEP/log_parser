from __future__ import annotations

from dataclasses import dataclass

from events.base_event import BaseEvent
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from router.router import EventRouter


@dataclass
class BaseProducer:
    _router: EventRouter = None

    def __init__(self):
        pass

    async def setup(self):
        pass

    async def produce(self) -> BaseEvent:
        pass

    async def _produce_events(self) -> None:
        while True:
            await self._router.route_event(await self.produce())
