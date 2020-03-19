import shutil
import tempfile
from pathlib import Path
from typing import List

from aiohttp import web

from aiohttp_tus import setup_tus


def create_app(argv: List[str] = None) -> web.Application:
    upload_path = Path(tempfile.gettempdir()) / "aiohttp-tus-app-uploads"
    upload_path.mkdir(mode=0o755, exist_ok=True)

    print("aiohttp_tus test app")
    print(f"Uploading files to {upload_path.absolute()}\n")

    app = setup_tus(web.Application(), upload_path=upload_path)

    app["aiohttp_tus_upload_path"] = upload_path
    app.on_shutdown.append(remove_upload_path)

    return app


async def remove_upload_path(app: web.Application) -> None:
    upload_path = app["aiohttp_tus_upload_path"]
    print(f"\nRemoving {upload_path.absolute()} directory")
    shutil.rmtree(upload_path)
