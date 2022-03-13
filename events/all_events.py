from os.path import dirname, basename, isfile, join
import glob
import importlib

from events.base_event import BaseEvent

_modules = glob.glob(join(dirname(__file__), "*.py"))
_module_names = [basename(f)[:-3] for f in _modules if isfile(f) and not f.endswith('__init__.py')]
_event_modules = [importlib.import_module('events.' + x) for x in _module_names]
_events = [
    [x for x in vars(module).values() if type(x) == type and issubclass(x, BaseEvent)]
    for module in _event_modules
]
events = set(sum(_events, []))
events = {x.__name__: x for x in events}