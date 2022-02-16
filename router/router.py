from __future__ import annotations
import asyncio
from typing import List, Awaitable, Dict, Type, Union, TYPE_CHECKING
from consumers.basic_consumer import SinkConsumer
if TYPE_CHECKING:
    from consumers.basic_node import BasicNode
    from events.base_event import BaseEvent
    from consumers.base_producer import BaseProducer


class EventRouter:
    node_list: List[BasicNode] = None
    _event_routing: Dict[Type[BaseEvent], List[SinkConsumer]] = None
    _sink: SinkConsumer = None

    def __init__(self, default: Type[SinkConsumer] = SinkConsumer):
        self.node_list = []

        self._event_routing = {}
        self._sink = default([])

    def run(self) -> Awaitable:
        """
        Use this to start all consumers and producers simultaneously
        :return:
        """
        return asyncio.gather(
            *[consumer._running_loop() for consumer in self.node_list])

    async def register_node(self, node: Union[BaseProducer, SinkConsumer]):
        try:
            # Try if this is a consumer
            await node._create_queue()
            for event in node.events_to_respond:
                self._event_routing[event] = self._event_routing.get(event, []) + [node]
        except AttributeError:
            # This was a producer
            pass
        finally:
            self.node_list.append(node)
            node._set_router(self)
            await node.setup()

    async def route_event(self, event: BaseEvent) -> None:
        """
        Find right consumer for an event `event` and add it to it's queue
        :param event:
        :return:
        """
        for consumer in self._event_routing.get(type(event), [self._sink]):
            await consumer.queue.put(event)




