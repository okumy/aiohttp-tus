import shutil
import tempfile
from pathlib import Path
from typing import List

import jinja2
from aiohttp import web
from aiohttp_jinja2 import setup as setup_jinja2

from aiohttp_tus import setup_tus
from . import views
from .constants import APP_UPLOAD_PATH_KEY
from .utils import get_client_max_size


def create_app(argv: List[str] = None) -> web.Application:
    upload_path = Path(tempfile.gettempdir()) / "aiohttp-tus-example-uploads"
    upload_path.mkdir(mode=0o755, exist_ok=True)

    app = setup_tus(
        web.Application(client_max_size=get_client_max_size()), upload_path=upload_path,
    )
    app[APP_UPLOAD_PATH_KEY] = upload_path
    setup_jinja2(
        app, loader=jinja2.FileSystemLoader(Path(__file__).parent / "templates")
    )

    app.router.add_get("/", views.index)
    app.on_shutdown.append(remove_upload_path)

    print("aiohttp-tus example app")
    print(f"Uploading files to {upload_path.absolute()}\n")

    return app


async def remove_upload_path(app: web.Application) -> None:
    upload_path = app[APP_UPLOAD_PATH_KEY]
    print(f"\nRemoving {upload_path.absolute()}")
    shutil.rmtree(upload_path)
