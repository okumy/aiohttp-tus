import tempfile
from functools import partial
from pathlib import Path

try:
    from contextlib import asynccontextmanager
except ImportError:
    from async_generator import asynccontextmanager

import pytest
import tus
from aiohttp import hdrs, web
from aiohttp.test_utils import TestClient

from aiohttp_tus import setup_tus
from aiohttp_tus.annotations import Decorator, Handler
from aiohttp_tus.constants import APP_TUS_CONFIG_KEY
from aiohttp_tus.data import TusConfig


SECRET_TOKEN = "secret-token"
TEST_DATA_PATH = Path(__file__).parent / "test-data"


@pytest.fixture
def aiohttp_test_client(aiohttp_client):
    @asynccontextmanager
    async def factory(
        *, upload_url: str, upload_suffix: str = None, decorator: Decorator = None
    ) -> TestClient:
        with tempfile.TemporaryDirectory(prefix="aiohttp_tus") as temp_path:
            base_path = Path(temp_path)
            app = setup_tus(
                web.Application(),
                upload_path=base_path / upload_suffix if upload_suffix else base_path,
                upload_url=upload_url,
                decorator=decorator,
            )
            yield await aiohttp_client(app)

    return factory


def get_upload_url(client: TestClient, upload_url: str) -> str:
    return f"http://{client.host}:{client.port}{upload_url}"


def login_required(handler: Handler) -> Handler:
    async def decorator(request: web.Request) -> web.StreamResponse:
        header = request.headers.get(hdrs.AUTHORIZATION)
        if header is None or header != f"Token {SECRET_TOKEN}":
            raise web.HTTPForbidden()
        return await handler(request)

    return decorator


async def test_decorated_upload_200(aiohttp_test_client, loop):
    async with aiohttp_test_client(
        upload_url="/uploads", decorator=login_required
    ) as client:
        upload = partial(
            tus.upload,
            file_name="hello.txt",
            headers={"Authorization": "Token secret-token"},
        )
        with open(TEST_DATA_PATH / "hello.txt", "rb") as handler:
            await loop.run_in_executor(
                None, upload, handler, get_upload_url(client, "/uploads")
            )


async def test_decorated_upload_403(aiohttp_test_client, loop):
    async with aiohttp_test_client(
        upload_url="/uploads", decorator=login_required
    ) as client:
        upload = partial(
            tus.upload,
            file_name="hello.txt",
            headers={"Authorization": "Token not-secret-token"},
        )
        with open(TEST_DATA_PATH / "hello.txt", "rb") as handler:
            with pytest.raises(tus.TusError):
                await loop.run_in_executor(
                    None, upload, handler, get_upload_url(client, "/uploads")
                )


@pytest.mark.parametrize(
    "upload_url, upload_suffix, tus_upload_url, match_info",
    (
        ("/uploads", None, "/uploads", {}),
        (r"/user/{username}/uploads", None, "/user/playpauseanddtop/uploads", {}),
        (
            r"/user/{username}/uploads",
            r"{username}",
            "/user/playpauseandstop/uploads",
            {"username": "playpauseandstop"},
        ),
    ),
)
async def test_upload(
    aiohttp_test_client, loop, upload_url, upload_suffix, tus_upload_url, match_info,
):
    async with aiohttp_test_client(
        upload_url=upload_url, upload_suffix=upload_suffix
    ) as client:
        test_upload_path = TEST_DATA_PATH / "hello.txt"

        upload = partial(tus.upload, file_name="hello.txt")
        with open(test_upload_path, "rb") as handler:
            await loop.run_in_executor(
                None, upload, handler, get_upload_url(client, tus_upload_url)
            )

        config: TusConfig = client.app[APP_TUS_CONFIG_KEY]
        expected_upload_path = config.resolve_upload_path(match_info) / "hello.txt"
        assert expected_upload_path.exists()
        assert expected_upload_path.read_bytes() == test_upload_path.read_bytes()
