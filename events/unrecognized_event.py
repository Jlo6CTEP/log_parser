from dataclasses import dataclass

from events.log_event import LogEvent


@dataclass
class UnrecognizedLogEvent(LogEvent):
    """
    This one will accept ANY log_message
    """
    message: str = None

    def __init__(self, log_message: str):
        super().__init__(log_message)
        self.message = log_message[self._start_index:].strip()
