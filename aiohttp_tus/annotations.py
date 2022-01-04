from typing import Any, Callable, Dict, Mapping

try:
    from aiohttp.web_middlewares import _Handler as Handler
except ImportError:
    from aiohttp.web_middlewares import Handler

Decorator = Callable[[Handler], Handler]

DictStrAny = Dict[str, Any]
DictStrBytes = Dict[str, bytes]
DictStrStr = Dict[str, str]

JsonDumps = Callable[[Any], str]
JsonLoads = Callable[[str], Any]

MappingStrBytes = Mapping[str, bytes]
MappingStrStr = Mapping[str, str]
