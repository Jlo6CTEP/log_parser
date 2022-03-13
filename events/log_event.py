import re
from dataclasses import dataclass, field, asdict
from datetime import datetime

from events.base_event import BaseEvent


@dataclass
class LogEvent(BaseEvent):
    source : str = field(default="")
    target: str = field(default="")
    _pattern_matcher: re.Pattern = field(default=re.compile(
        ".*(?P<tstamp>\\[\d\d:\d\d:\d\d]) (?P<src>\\[[^]]*]): (?P<tgt>\\[[^]]*])?"),
    repr=False, metadata={'dict': False})
    _start_index: int = field(default=0, repr=False, metadata={'dict': False})

    def __init__(self, log_message: str):
        """
        Raise AttributeError if message does not fit this Event
        i.e. _pattern_matcher matches nothing
        :param log_message: message to be transformed into Event
        """
        # Class name used to properly combine subsequent Event's matchers
        match_group = LogEvent._pattern_matcher.match(log_message)
        self.timestamp = datetime.strptime(
            match_group.group('tstamp'), "[%H:%M:%S]").time()
        self.source = match_group.group('src').strip()[1:-1]  # this gets rid of []
        self.target = match_group.group('tgt')

        if self.target:
            self.target = self.target.strip()[1:-1]  # this gets rid of []
        self._start_index = match_group.end()