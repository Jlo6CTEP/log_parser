import asyncio
from asyncio.subprocess import Process
from dataclasses import dataclass, field

from events.base_event import BaseEvent
from events.event_factory import LogEventFactory
from producers.base_producer import BaseProducer
from router.router import EventRouter

DIRECTORY = r"~\AppData\Roaming\.vimeworld\minigames\logs"


@dataclass
class GetContentProducer(BaseProducer):
    _router: EventRouter = field(init=False)
    factory: LogEventFactory = field(init=False)
    proc: Process = field(default=None, init=False)

    def __init__(self, event_factory: LogEventFactory):
        super().__init__()
        self.factory = event_factory

    async def setup(self):
        self.proc = await asyncio.create_subprocess_shell(
            rf"Powershell Get-Content {DIRECTORY}\latest.log -Tail 10 -Wait",
            stdout=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE
        )

    async def produce(self) -> BaseEvent:
        line = (await self.proc.stdout.readline()).decode('utf-8').strip()
        return self.factory.process_message(line)
