from dataclasses import dataclass, asdict, fields, field, MISSING
from datetime import datetime


@dataclass
class BaseEvent:
    timestamp : datetime.time = field(default_factory=datetime.now().time)

    def to_dict(self):
        d = asdict(self)
        for field in fields(self):
            if not field.metadata.get('dict', True):
                d.pop(field.name)
        return d

    @classmethod
    def from_dict(cls, **kwargs):
        obj = cls.__new__(cls)  # Does not call __init__
        for field in fields(obj):
            if field.metadata.get('dict', True):
                if field.default != MISSING:
                    value = field.default
                elif field.default_factory != MISSING:
                    value = field.default_factory()
                else:
                    value = None
                obj.__setattr__(field.name, kwargs.get(field.name, value))
        return obj
