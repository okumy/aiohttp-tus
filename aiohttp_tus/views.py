import logging

import attr
from aiohttp import web

from . import constants
from .annotations import DictStrStr
from .data import get_config, Resource
from .utils import (
    get_resource_or_404,
    get_resource_or_410,
    on_upload_done,
    parse_upload_metadata,
)
from .validators import check_file_name, validate_upload_metadata


logger = logging.getLogger(__name__)


async def delete_resource(request: web.Request) -> web.Response:
    """Delete resource if user canceled the upload."""
    # Ensure resource exists
    resource = get_resource_or_404(request)

    # Remove resource file and its metadata
    config = get_config(request)
    match_info = request.match_info
    resource.delete(config=config, match_info=match_info)
    resource.delete_metadata(config=config, match_info=match_info)

    return web.Response(status=204, headers=constants.BASE_HEADERS)


async def resource_details(request: web.Request) -> web.Response:
    """Request resource offset if it is present."""
    # Ensure resource exists
    resource = get_resource_or_404(request)
    return web.Response(
        status=200,
        text="",
        headers={
            **constants.BASE_HEADERS,
            constants.HEADER_CACHE_CONTROL: "no-store",
            constants.HEADER_UPLOAD_OFFSET: str(resource.offset),
            constants.HEADER_UPLOAD_LENGTH: str(resource.file_size),
        },
    )


async def start_upload(request: web.Request) -> web.Response:
    """Start uploading file with tus protocol."""
    # Ensure Tus-Resumable header exists
    if not request.headers.get(constants.HEADER_TUS_RESUMABLE):
        logger.warning(
            "Wrong headers for start upload view", extra={"headers": request.headers}
        )
        raise web.HTTPInternalServerError(
            text="Received file upload for unsupported file transfer protocol"
        )

    config = get_config(request)
    headers = constants.BASE_HEADERS.copy()

    # Ensure upload metadata header is valid one
    metadata_header = request.headers.get(constants.HEADER_UPLOAD_METADATA) or ""
    valid_metadata = validate_upload_metadata(parse_upload_metadata(metadata_header))
    file_name = check_file_name(valid_metadata, config=config)

    # If file name already exists in the storage - do not allow attempt to overwrite it
    if file_name and not config.allow_overwrite_files:
        raise web.HTTPConflict(headers=headers)

    if not file_name:
        file_name = valid_metadata["filename"].decode()

    # Prepare resource for the upload
    resource = Resource(
        file_name=file_name,
        file_size=int(request.headers.get(constants.HEADER_UPLOAD_LENGTH) or 0),
        offset=0,
        metadata_header=metadata_header,
    )

    # Save resource and its metadata
    match_info = request.match_info
    try:
        resource.save(config=config, match_info=match_info, chunk=b"\0")
        resource.save_metadata(config=config, match_info=match_info)
    # In case if file system is not able to store given files - abort the upload
    except IOError:
        logger.error(
            "Unable to create file",
            exc_info=True,
            extra={
                "file_name": file_name,
                "resource": attr.asdict(resource),
                "upload_path": config.upload_path.absolute(),
            },
        )
        raise web.HTTPInternalServerError(
            text="Unexpected error on uploading file", headers=headers
        )

    # Specify resource headers for tus client
    headers[constants.HEADER_LOCATION] = str(
        request.url.join(
            request.app.router[config.resource_tus_resource_name].url_for(
                **request.match_info, resource_uid=resource.uid
            )
        )
    )
    headers[constants.HEADER_TUS_TEMP_FILENAME] = resource.uid

    return web.Response(status=201, text="", headers=headers)


async def upload_details(request: web.Request) -> web.Response:
    """Check whether requested filename already started to upload or not."""
    valid_metadata = validate_upload_metadata(parse_upload_metadata(request.headers))
    file_name = check_file_name(valid_metadata, config=get_config(request))

    headers: DictStrStr = {}
    if file_name is not None:
        headers[constants.HEADER_TUS_FILE_EXISTS] = "true"
        headers[constants.HEADER_TUS_FILE_NAME] = file_name
    else:
        headers[constants.HEADER_TUS_FILE_EXISTS] = "false"

    return web.Response(status=200, text="", headers=headers)


async def upload_options(request: web.Request) -> web.Response:
    """List tus protocol supported options."""
    if not request.headers.get(constants.HEADER_TUS_RESUMABLE):
        return web.Response(status=200, text="")
    return web.Response(
        status=204,
        headers={
            **constants.BASE_HEADERS,
            constants.HEADER_TUS_EXTENSION: ",".join(constants.TUS_API_EXTENSIONS),
            constants.HEADER_TUS_MAX_SIZE: str(constants.TUS_MAX_FILE_SIZE),
        },
    )


async def upload_resource(request: web.Request) -> web.Response:
    """Upload resource chunk.

    Read resource metadata and save another chunk to the resource. If this is a final
    chunk, move resource to original file name and remove resource metadata.
    """
    # Ensure resource metadata is readable and resource file exists as well
    resource = get_resource_or_410(request)

    # Ensure resource offset equals to expected upload offset
    upload_offset = int(request.headers.get(constants.HEADER_UPLOAD_OFFSET) or 0)
    if upload_offset != resource.offset:
        raise web.HTTPConflict(headers=constants.BASE_HEADERS)

    # Save current chunk to the resource
    config = get_config(request)
    match_info = request.match_info
    resource.save(config=config, match_info=match_info, chunk=await request.read())

    # If this is a final chunk - complete upload
    chunk_size = int(request.headers.get(constants.HEADER_CONTENT_LENGTH) or 0)
    next_offset = resource.offset + chunk_size
    if next_offset == resource.file_size:
        file_path = resource.complete(config=config, match_info=match_info)
        await on_upload_done(
            request=request, config=config, resource=resource, file_path=file_path
        )
    # But if it is not - store new metadata
    else:
        next_resource = attr.evolve(resource, offset=next_offset)
        next_resource.save_metadata(config=config, match_info=match_info)

    # Return upload headers
    return web.Response(
        status=204,
        headers={
            **constants.BASE_HEADERS,
            constants.HEADER_TUS_TEMP_FILENAME: resource.uid,
            constants.HEADER_UPLOAD_OFFSET: str(next_offset),
        },
    )
