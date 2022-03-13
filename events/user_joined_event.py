import re
from dataclasses import dataclass, field

from events.log_event import LogEvent


@dataclass
class UserJoinedLogEvent(LogEvent):
    """
    This one will accept ANY log_message
    """
    tag: str = field(default="")
    nick: str = field(default="")

    _pattern_matcher = re.compile("\\+ (?P<tag>\\[[^]]{1,4}]) (?P<nick>\w+)")

    def __init__(self, log_message: str):
        super().__init__(log_message)
        group_match = self._pattern_matcher.match(
            log_message[self._start_index:].strip())

        self.tag = group_match.group('tag')[1:-1]  # get rid of []
        self.nick = group_match.group('nick')
