from dataclasses import dataclass
from typing import List, Type

from consumers.basic_consumer import SinkConsumer
from events.base_event import BaseEvent
from events.user_joined_event import UserJoinedLogEvent
from logging_facility import logger


@dataclass
class UserJoinedEventConsumer(SinkConsumer):

    def __init__(self, events_to_respond: List[Type[BaseEvent]]):
        super().__init__(events_to_respond)

    async def process(self, item: UserJoinedLogEvent) -> None:
        logger.debug(f"User {item.nick} joined")
