from typing import Any, Callable, Dict, Mapping

from aiohttp.web_middlewares import _Handler as Handler


Decorator = Callable[[Handler], Handler]

DictStrAny = Dict[str, Any]
DictStrBytes = Dict[str, bytes]
DictStrStr = Dict[str, str]

MappingStrBytes = Mapping[str, bytes]
MappingStrStr = Mapping[str, str]
