from __future__ import annotations

import asyncio
from typing import List, Dict, Type

from events.base_event import BaseEvent
from nodes.basic_nodes import BaseConsumer
from nodes.basic_nodes import BaseNode


class EventRouter:
    node_list: List[BaseNode] = None
    _local_event_routing: Dict[Type[BaseEvent], List[BaseNode]] = None
    _sink: BaseConsumer = None

    def __init__(self, default: Type[BaseConsumer] = BaseConsumer):
        self.node_list = []

        self._local_event_routing = {}
        self._sink = default([])
        self._sink._set_router(self)

    async def run(self) -> None:
        """
        Use this to start all nodes simultaneously.
        Blocking
        :return:
        """
        await self._sink.setup()
        await asyncio.gather(
            *[node._running_loop() for node in self.node_list],
            self._sink._running_loop()
        )

    async def register_node(self, node: BaseNode) -> None:
        for event in node.events_to_respond:
            self._local_event_routing[event] = \
                self._local_event_routing.get(event, []) + [node]
        self.node_list.append(node)
        node._set_router(self)
        await node.setup()

    async def unregister_node(self, node: BaseNode) -> None:
        for event in node.events_to_respond:
            self._local_event_routing[event].remove(node)
        self.node_list.remove(node)

    def route_event(self, event: BaseEvent) -> None:
        """
        Find right node for an event `event` and add it to it's queue
        :param event:
        :return:
        """
        for node in self._local_event_routing.get(type(event), [self._sink]):
            asyncio.create_task(node.enqueue_event(event))




