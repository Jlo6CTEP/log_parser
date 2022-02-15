from __future__ import annotations
import asyncio
from typing import List, Awaitable, Dict, Type
from consumers.basic_consumer import SinkConsumer
from events.base_event import BaseEvent
from producers.base_producer import BaseProducer


class EventRouter:
    consumer_list: List[SinkConsumer] = None
    producer_list: List[BaseProducer]
    _event_routing: Dict[Type[BaseEvent], List[SinkConsumer]] = None
    _sink: SinkConsumer = None

    def __init__(self, default: Type[SinkConsumer] = SinkConsumer):
        self.consumer_list = []
        self.producer_list = []

        self._event_routing = {}
        self._sink = default([])

    def run(self) -> Awaitable:
        """
        Use this to start all consumers and producers simultaneously
        :return:
        """
        return asyncio.gather(
            *[consumer._process_events() for consumer in self.consumer_list],
            *[producer._produce_events() for producer in self.producer_list])

    async def register_consumer(self, consumer: SinkConsumer):
        await consumer._create_queue()
        self.consumer_list.append(consumer)
        for event in consumer.events_to_respond:
            self._event_routing[event] = self._event_routing.get(event, []) + [consumer]
        consumer._router = self

    async def register_producer(self, producer: BaseProducer):
        self.producer_list.append(producer)
        producer._router = self
        await producer.setup()

    async def route_event(self, event: BaseEvent) -> None:
        """
        Find right consumer for an event `event` and add it to it's queue
        :param event:
        :return:
        """
        for consumer in self._event_routing.get(type(event), [self._sink]):
            await consumer.queue.put(event)




