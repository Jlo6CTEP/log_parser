from __future__ import annotations
from typing import List, Type

from events.log_event import LogEvent
from events.unrecognized_event import UnrecognizedLogEvent


class LogEventFactory:
    event_classes = None

    def __init__(self):
        self.event_classes: List[Type[LogEvent]] = []

    def register_event_type(self, event_cls: Type[LogEvent]) -> None:
        self.event_classes.append(event_cls)

    def process_message(self, log_message: str) -> LogEvent:
        for event_class in self.event_classes:
            try:
                event = event_class(log_message)
                break
            except AttributeError:
                pass
        else:
            # if the right event type is found, we will break out of for loop
            # and newer get there
            event = UnrecognizedLogEvent(log_message)
        return event
