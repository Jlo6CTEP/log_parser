import asyncio
from typing import List, Awaitable, Dict, Type

from consumers.basic_consumer import SinkConsumer
from events.base_event import BaseEvent


class ConsumerEventRouter:
    consumer_list = None
    _event_routing: Dict[Type[BaseEvent], List[SinkConsumer]] = None
    _sink: SinkConsumer = None

    def __init__(self, consumers: List[SinkConsumer],
                 default: Type[SinkConsumer] = SinkConsumer):
        self.consumer_list = consumers
        self._event_routing = {}

        # build event routing dictionary
        for consumer in self.consumer_list:
            for event in consumer.events_to_respond:
                self._event_routing[event] = \
                    self._event_routing.get(event, []) + [consumer]

        self._sink = default([])

    async def gather(self) -> Awaitable:
        return asyncio.gather(*[
            consumer._consume_from_queue() for consumer in self.consumer_list])

    async def route_event(self, event) -> Awaitable:
        return asyncio.gather(*[
            consumer.process_event(event) for consumer in
            self._event_routing.get(type(event), [self._sink])
        ])




