import json
from pathlib import Path

from aiohttp import web

from . import views
from .annotations import Decorator, Handler, JsonDumps, JsonLoads
from .constants import APP_TUS_CONFIG_KEY
from .data import Config, get_resource_url, ResourceCallback, set_config


def setup_tus(
    app: web.Application,
    *,
    upload_path: Path,
    upload_url: str = "/uploads",
    upload_resource_name: str = None,
    allow_overwrite_files: bool = False,
    decorator: Decorator = None,
    on_upload_done: ResourceCallback = None,
    json_dumps: JsonDumps = json.dumps,
    json_loads: JsonLoads = json.loads,
) -> web.Application:
    """Setup tus protocol server implementation for aiohttp.web application.

    It is a cornerstone of ``aiohttp-tus`` library and in most cases only thing
    developers need to know for setting up tus.io server for aiohttp.web application.

    :param app: :class:`aiohttp.web.Application` instance
    :param upload_path:
        :class:`pathlib.Path` instance to point the directory where to store uploaded
        files. Please, esnure that given directory is exists before application start
        and is writeable for current user.

        It is possible to prepend any ``match_info`` param from named URL.
    :param upload_url:
        tus.io upload URL. Can be plain as ``/uploads`` or named as
        ``/users/{username}/uploads``. By default: ``"/uploads"``
    :param upload_resource_name:
        By default ``aiohttp-tus`` will provide auto name for the upload resource, as
        well as for the chunk resource. But sometimes it might be useful to provide
        exact name, which can lately be used for URL reversing.
    :param allow_overwrite_files:
        When enabled allow to overwrite already uploaded files. This may harm
        consistency of stored data, cause please use this param with caution. By
        default: ``False``
    :param decorator:
        In case of guarding upload views it might be useful to decorate them with
        given decorator function. By default: ``None`` (which means **ANY** client will
        able to upload files)
    :param on_upload_done:
        Coroutine to call after upload is done. Coroutine will receive three arguments:
        ``request``, ``resource`` & ``file_path``. Request is current
        :class:`aiohttp.web.Request` instance. Resource will contain all data about
        uploaded resource such as file name, file size
        (:class:`aiohttp_tus.data.Resource` instance). While file path will contain
        :class:`pathlib.Path` instance of uploaded file.
    :param json_dumps:
        To store resource metadata between chunk uploads ``aiohttp-tus`` using JSON
        files, stored into ``upload_path / ".metadata"`` directory.

        To dump the data builtin Python function used: :func:`json.dumps`, but you
        might customize things if interested in using ``ujson``, ``orjson``,
        ``rapidjson`` or other implementation.
    :param json_loads:
        Similarly to ``json_dumps``, but for loading data from JSON metadata files.
        By default: :func:`json.loads`
    """

    def decorate(handler: Handler) -> Handler:
        if decorator is None:
            return handler
        return decorator(handler)

    # Ensure support of multiple tus upload URLs for one application
    app.setdefault(APP_TUS_CONFIG_KEY, {})

    # Need to find out canonical dynamic resource URL if any and use it for storing
    # tus config into the app
    canonical_upload_url = web.DynamicResource(upload_url).canonical

    # Store tus config in application
    config = Config(
        upload_path=upload_path,
        upload_url=upload_url,
        upload_resource_name=upload_resource_name,
        allow_overwrite_files=allow_overwrite_files,
        on_upload_done=on_upload_done,
        json_dumps=json_dumps,
        json_loads=json_loads,
    )
    set_config(app, canonical_upload_url, config)

    # Views for upload management
    upload_resource = app.router.add_resource(
        upload_url, name=config.resource_tus_upload_name
    )
    upload_resource.add_route("OPTIONS", views.upload_options)
    upload_resource.add_route("GET", decorate(views.upload_details))
    upload_resource.add_route("POST", decorate(views.start_upload))

    # Views for resource management
    resource_resource = app.router.add_resource(
        get_resource_url(upload_url), name=config.resource_tus_resource_name
    )
    resource_resource.add_route("HEAD", decorate(views.resource_details))
    resource_resource.add_route("DELETE", decorate(views.delete_resource))
    resource_resource.add_route("PATCH", decorate(views.upload_resource))

    return app
