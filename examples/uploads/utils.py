import os

import humanfriendly

from .constants import DEFAULT_CLIENT_MAX_SIZE


def get_client_max_size() -> int:
    return humanfriendly.parse_size(  # type: ignore
        os.getenv("AIOHTTP_CLIENT_MAX_SIZE") or DEFAULT_CLIENT_MAX_SIZE
    )
