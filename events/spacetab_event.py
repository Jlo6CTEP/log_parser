from dataclasses import dataclass, field
from typing import List
import re

from events.log_event import LogEvent


@dataclass
class SpaceTabLogEvent(LogEvent):
    nicknames_list: List[str] = None

    _pattern_matcher: re.Pattern = field(
        default=re.compile("(\w+, )+(\w+)$"), repr=False
    )

    def __init__(self, log_message: str):
        super().__init__(log_message)
        match_group = SpaceTabLogEvent._pattern_matcher.match(
            log_message[self._start_index:].strip())
        self.nicknames_list = match_group.group().split(', ')
