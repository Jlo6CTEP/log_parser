from __future__ import annotations
import asyncio
from datetime import datetime

from consumers.basic_consumer import SinkConsumer
from consumers.GetContent_producer import GetContentProducer
from router.router import EventRouter
from consumers.ping import PingEventConsumer
from consumers.pong import PongEventConsumer
from consumers.space_tab_event_consumer import SpaceTabEventConsumer
from consumers.user_joined_consumer import UserJoinedEventConsumer
from events.event_factory import LogEventFactory
from events.ping import PingEvent, PongEvent
from events.spacetab_event import SpaceTabLogEvent
from events.unrecognized_event import UnrecognizedLogEvent
from events.user_joined_event import UserJoinedLogEvent

DIRECTORY = r"~\AppData\Roaming\.vimeworld\minigames\logs"


async def main():
    factory = LogEventFactory()
    factory.register_event_type(SpaceTabLogEvent)
    factory.register_event_type(UserJoinedLogEvent)

    space_tab_consumer = SpaceTabEventConsumer([SpaceTabLogEvent])
    sink_consumer = SinkConsumer([UnrecognizedLogEvent])
    user_joined_consumer = UserJoinedEventConsumer([UserJoinedLogEvent])
    ping = PingEventConsumer([PingEvent])
    pong = PongEventConsumer([PongEvent])

    producer = GetContentProducer(factory)
    router = EventRouter()

    await router.register_node(space_tab_consumer)
    await router.register_node(sink_consumer)
    await router.register_node(user_joined_consumer)
    await router.register_node(ping)
    await router.register_node(pong)

    await router.register_node(producer)

    await router.route_event(PingEvent(datetime.now().time(), "ping"))
    await router.run()


loop = asyncio.ProactorEventLoop()
loop.set_debug(True)
asyncio.set_event_loop(loop)
loop.run_until_complete(main())
loop.close()
