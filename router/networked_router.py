from __future__ import annotations

import asyncio
import select
from asyncio import gather, AbstractEventLoop, sleep
from datetime import datetime
from threading import Thread
from typing import Dict, Type, Set, Union

import Pyro5.api
import Pyro5.core
import Pyro5.nameserver
from Pyro5.client import Proxy
from Pyro5.server import Daemon
from dacite import from_dict, Config

from events.all_events import events
from events.base_event import BaseEvent
from events.ping import PingEvent
from logging_facility import logger
from nodes.basic_nodes import BaseNode
from router.router import EventRouter


class NetworkedEventRouter(EventRouter):
    # This name should be UNIQUE across the computational network
    name: str = None
    routers: Set[Router]
    _global_event_routing: Dict[Type[BaseEvent], Set[Router]]
    _pyroUri: str = ""
    _event_loop: AbstractEventLoop = None

    def __init__(self, name):
        super().__init__()
        # Transfer event types (used as keys for routing) and instances,
        # which are events themselves, across the connection in one go
        for event in events.values():
            Pyro5.api.register_class_to_dict(
                event,
                lambda x: {**x.to_dict(), **{'__class__': event.__name__}})
            Pyro5.api.register_dict_to_class(
                event.__name__,
                lambda cls, x: events[cls].from_dict(**x)
            )

        Pyro5.api.register_class_to_dict(
            type,
            lambda x: {'name': x.__name__, "__class__": "type"}
        )
        Pyro5.api.register_dict_to_class(
            "type",
            lambda _, x: events[x['name']]
        )
        self.name = name
        self.routers = {self}
        self._global_event_routing = {}
        self._event_loop = asyncio.get_running_loop()

    @property
    @Pyro5.api.expose
    def local_routing_table(self):
        return list(self._local_event_routing.keys())

    @property
    @Pyro5.api.expose
    def global_routing_table(self):
        return list(self._global_event_routing.keys())

    @Pyro5.api.expose
    def connect_router(self, router: Proxy):
        logger.debug(f"Router {router._pyroUri} connected")
        self.notify_routers_add(router)

        for other_router in self.routers:
            if other_router._pyroUri == self._pyroUri:
                continue

            logger.debug(f"Notifying {other_router._pyroUri} about new router")
            with Proxy(other_router._pyroUri) as router_to_notify:
                router_to_notify.notify_routers_add(router)

    @Pyro5.api.expose
    def disconnect_router(self, router: Proxy):
        logger.debug(f"Router {router._pyroUri} disconnected")
        self.notify_routers_del(router)

        for other_router in self.routers:
            if other_router._pyroUri == self._pyroUri:
                continue
            logger.debug(f"Notifying {other_router._pyroUri} about left router")
            with Proxy(other_router._pyroUri) as router_to_notify:
                router_to_notify.notify_routers_del(router)

    @Pyro5.server.oneway
    @Pyro5.api.expose
    def route_event(self, event: BaseEvent):
        for router in self._global_event_routing.get(type(event), [self]):
            if isinstance(router, Proxy):
                # If router that serves this message type is a proxy
                # Then just route it
                with Proxy(router._pyroUri) as r:
                    r.route_event(event)
            else:
                try:
                    # If this method was called from Pyro daemon, there ain`t
                    # gonna be no running event loop
                    asyncio.get_running_loop()
                    super(NetworkedEventRouter, router).route_event(event)
                except RuntimeError:
                    # So call threadsafe version of this method
                    self._route_event_threadsafe(event)

    def _route_event_threadsafe(self, event):
        for node in self._local_event_routing.get(type(event), [self._sink]):
            asyncio.run_coroutine_threadsafe(
                node.enqueue_event(event), self._event_loop).result()

    @Pyro5.api.expose
    def notify_routers_add(self, router: Proxy):
        logger.debug(f"Adding {router._pyroUri} to routing table")
        with Proxy(router._pyroUri) as r:
            self.routers.add(router)
            for event in router.local_routing_table:
                listeners = self._global_event_routing.get(event, set())
                listeners.add(router)
                self._global_event_routing[event] = listeners

    @Pyro5.api.expose
    def notify_routers_del(self, router: Proxy):
        logger.debug(f"Deleting {router._pyroUri} from routing table")
        with Proxy(router._pyroUri) as router:
            self.routers.remove(router)
            for event in router.local_routing_table:
                self._global_event_routing[event].remove(router)
    
    async def register_node(self, node: BaseNode) -> None:
        await super(NetworkedEventRouter, self).register_node(node)
        for event in node.events_to_respond:
            self._global_event_routing[event] = {self}

    def __hash__(self):
        return hash(self._pyroUri)


Router = Union[NetworkedEventRouter, Proxy]


class Runner:
    ns: Proxy = None
    daemon: Daemon = None
    router: Router = None
    ns_host: str = None
    ns_port: int = None

    def __init__(self, router: Router, host: str = "localhost", port: int = 54321,
                 ns_host: str = "localhost", ns_port: int = 54322):
        self.ns_host = ns_host
        self.ns_port = ns_port
        self.router = router
        self.daemon = Pyro5.api.Daemon(host, port)

    async def run(self):
        uri = self.daemon.register(self.router)
        self.ns = Pyro5.core.locate_ns(self.ns_host, self.ns_port)
        self.ns.register(self.router.name, uri)

        server_thread = Thread(target=self.daemon.requestLoop)
        server_thread.start()


class NameserverRunner(Runner):
    def __init__(self, router: Router, *args, **kwargs):
        super().__init__(router, *args, **kwargs)
        ns_thread = Thread(target=Pyro5.nameserver.start_ns_loop,
                           kwargs={'host': self.ns_host, 'port': self.ns_port})
        ns_thread.start()

    async def run(self):
        await super(NameserverRunner, self).run()
        await sleep(5)
        self.router.route_event(PingEvent(datetime.now().time(), "ping"))
        await self.router.run()


class ClientRunner(Runner):
    connect_to_uri: str = None

    def __init__(self, router: Router, connect_to_uri: str, *args, **kwargs):
        super().__init__(router, *args, **kwargs)
        self.connect_to_uri = connect_to_uri

    async def run(self):
        await super(ClientRunner, self).run()
        connect_to = self.ns.lookup(self.connect_to_uri)
        with Proxy(connect_to) as proxy:
            proxy.connect_router(self.router)
        await self.router.run()



