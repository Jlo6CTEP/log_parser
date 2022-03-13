from __future__ import annotations

import asyncio

from events.event_factory import LogEventFactory
from events.spacetab_event import SpaceTabLogEvent
from events.user_joined_event import UserJoinedLogEvent
from nodes.GetContent_producer import GetContentProducer
from nodes.space_tab_event_consumer import SpaceTabEventConsumer
from nodes.user_joined_consumer import UserJoinedEventConsumer
from router.router import EventRouter

DIRECTORY = r"~\AppData\Roaming\.vimeworld\minigames\logs"


async def main():
    space_tab_consumer = SpaceTabEventConsumer([SpaceTabLogEvent])
    user_joined_consumer = UserJoinedEventConsumer([UserJoinedLogEvent])

    factory = LogEventFactory()
    factory.register_event_type(SpaceTabLogEvent)
    factory.register_event_type(UserJoinedLogEvent)
    producer = GetContentProducer(factory)

    router = EventRouter()

    await router.register_node(user_joined_consumer)
    await router.register_node(producer)
    await router.register_node(space_tab_consumer)
    await router.run()


loop = asyncio.ProactorEventLoop()
loop.set_debug(True)
asyncio.set_event_loop(loop)
loop.run_until_complete(main())
loop.close()
