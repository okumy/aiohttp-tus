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
    allow_overwrite_files: bool = False,
    decorator: Decorator = None,
    on_upload_done: ResourceCallback = None,
    json_dumps: JsonDumps = json.dumps,
    json_loads: JsonLoads = json.loads,
) -> web.Application:
    """Setup tus protocol server implementation for aiohttp.web application."""

    def decorate(handler: Handler) -> Handler:
        if decorator is None:
            return handler
        return decorator(handler)

    # Ensure support of multiple tus upload URLs for one application
    app.setdefault(APP_TUS_CONFIG_KEY, {})

    # Store tus config in application
    config = Config(
        upload_path=upload_path,
        upload_url=upload_url,
        allow_overwrite_files=allow_overwrite_files,
        on_upload_done=on_upload_done,
        json_dumps=json_dumps,
        json_loads=json_loads,
    )
    set_config(app, upload_url, config)

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
