from __future__ import annotations
import asyncio
import subprocess

from consumers.basic_consumer import SinkConsumer
from consumers.consumer_router import ConsumerEventRouter
from consumers.space_tab_event_consumer import SpaceTabEventConsumer
from consumers.user_joined_consumer import UserJoinedEventConsumer
from events.event_factory import LogEventFactory
from events.spacetab_event import SpaceTabLogEvent
from events.unrecognized_event import UnrecognizedLogEvent
from events.user_joined_event import UserJoinedLogEvent

DIRECTORY = r"C:\Users\ysuho\AppData\Roaming\.vimeworld\minigames\logs"


async def get_content():
    proc = await asyncio.create_subprocess_shell(
        rf"Powershell Get-Content {DIRECTORY}\latest.log -Tail 10 -Wait",
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    while True:
        line = (await proc.stdout.readline()).decode('utf-8').strip()
        event = factory.process_message(line)
        await router.route_event(event)


factory = LogEventFactory()
factory.register_event_type(SpaceTabLogEvent)
factory.register_event_type(UserJoinedLogEvent)

space_tab_consumer = SpaceTabEventConsumer([SpaceTabLogEvent])
sink_consumer = SinkConsumer([UnrecognizedLogEvent])
user_joined_consumer = UserJoinedEventConsumer([UserJoinedLogEvent])

router = ConsumerEventRouter([
    space_tab_consumer,
    sink_consumer,
    user_joined_consumer
])


loop = asyncio.ProactorEventLoop()
loop.set_debug(True)
asyncio.set_event_loop(loop)
loop.run_until_complete(asyncio.gather(
    get_content(),
    router.gather()
))
loop.close()