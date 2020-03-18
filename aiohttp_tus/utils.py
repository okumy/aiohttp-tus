import base64
import logging
from pathlib import Path

from aiohttp import web
from multidict import CIMultiDict

from .annotations import DictStrBytes, MappingStrBytes
from .data import Config, get_config, get_resource_path, Resource


logger = logging.getLogger(__name__)


def get_resource(request: web.Request) -> Resource:
    return Resource.from_metadata(
        config=get_config(request), match_info=request.match_info,
    )


def get_resource_or_404(request: web.Request) -> Resource:
    try:
        return get_resource(request)
    except IOError:
        logger.warning(
            "Unable to read resource metadata by requested UID",
            extra={"resource_uid": request.match_info["resource_uid"]},
        )
        raise web.HTTPNotFound(text="")


def get_resource_or_410(request: web.Request) -> Resource:
    try:
        resource = get_resource(request)
        if not get_resource_path(
            config=get_config(request), match_info=request.match_info, uid=resource.uid
        ).exists():
            raise IOError(f"{resource.uid} does not exist")
    except IOError:
        logger.warning(
            "Attempt to continue upload of removed resource",
            extra={"file_name" "resource_uid": resource.uid},
        )
        raise web.HTTPGone(text="")
    return resource


async def on_upload_done(
    *, request: web.Request, config: Config, resource: Resource, file_path: Path
) -> None:
    if not config.on_upload_done:
        return

    await config.on_upload_done(request, resource, file_path)


def parse_upload_metadata(metadata_header: str) -> MappingStrBytes:
    metadata: DictStrBytes = {}

    for item in metadata_header.split(","):
        if not item:
            continue
        key, value = item.split()
        metadata[key] = base64.b64decode(value)

    return CIMultiDict(metadata)
