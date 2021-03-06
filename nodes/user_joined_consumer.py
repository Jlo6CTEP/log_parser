from dataclasses import dataclass
from typing import List, Type

from nodes.basic_nodes import BaseConsumer
from events.base_event import BaseEvent
from events.user_joined_event import UserJoinedLogEvent
from logging_facility import logger


@dataclass
class UserJoinedEventConsumer(BaseConsumer):

    def __init__(self, events_to_respond: List[Type[BaseEvent]]):
        super().__init__(events_to_respond)

    async def process(self, item: UserJoinedLogEvent) -> None:
        logger.debug(f"User {item.nick} joined")
