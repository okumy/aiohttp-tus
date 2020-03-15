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
from aiohttp_tus.data import Config, ResourceCallback
from tests.common import (
    get_upload_url,
    TEST_CHUNK_SIZE,
    TEST_FILE_NAME,
    TEST_FILE_PATH,
    TEST_SCREENSHOT_NAME,
    TEST_SCREENSHOT_PATH,
    TEST_UPLOAD_URL,
)


SECRET_TOKEN = "secret-token"


@pytest.fixture
def aiohttp_test_client(aiohttp_client):
    @asynccontextmanager
    async def factory(
        *,
        upload_url: str,
        upload_suffix: str = None,
        allow_overwrite_files: bool = False,
        on_upload_done: ResourceCallback = None,
        decorator: Decorator = None,
    ) -> TestClient:
        with tempfile.TemporaryDirectory(prefix="aiohttp_tus") as temp_path:
            base_path = Path(temp_path)
            app = setup_tus(
                web.Application(),
                upload_path=base_path / upload_suffix if upload_suffix else base_path,
                upload_url=upload_url,
                allow_overwrite_files=allow_overwrite_files,
                on_upload_done=on_upload_done,
                decorator=decorator,
            )
            yield await aiohttp_client(app)

    return factory


def login_required(handler: Handler) -> Handler:
    async def decorator(request: web.Request) -> web.StreamResponse:
        header = request.headers.get(hdrs.AUTHORIZATION)
        if header is None or header != f"Token {SECRET_TOKEN}":
            raise web.HTTPForbidden()
        return await handler(request)

    return decorator


async def test_decorated_upload_200(aiohttp_test_client, loop):
    upload = partial(
        tus.upload,
        file_name=TEST_FILE_NAME,
        headers={"Authorization": "Token secret-token"},
    )

    async with aiohttp_test_client(
        upload_url=TEST_UPLOAD_URL, decorator=login_required
    ) as client:
        with open(TEST_FILE_PATH, "rb") as handler:
            await loop.run_in_executor(
                None, upload, handler, get_upload_url(client, TEST_UPLOAD_URL)
            )


async def test_decorated_upload_403(aiohttp_test_client, loop):
    upload = partial(
        tus.upload,
        file_name=TEST_FILE_NAME,
        headers={"Authorization": "Token not-secret-token"},
    )

    async with aiohttp_test_client(
        upload_url=TEST_UPLOAD_URL, decorator=login_required
    ) as client:
        with open(TEST_FILE_PATH, "rb") as handler:
            with pytest.raises(tus.TusError):
                await loop.run_in_executor(
                    None, upload, handler, get_upload_url(client, TEST_UPLOAD_URL)
                )


async def test_on_upload_callback(aiohttp_test_client, loop):
    data = {}
    upload = partial(tus.upload, file_name=TEST_FILE_NAME)

    async def on_upload_done(resource, file_path):
        data[resource.file_name] = file_path

    async with aiohttp_test_client(
        upload_url=TEST_UPLOAD_URL, on_upload_done=on_upload_done
    ) as client:
        with open(TEST_FILE_PATH, "rb") as handler:
            await loop.run_in_executor(
                None, upload, handler, get_upload_url(client, TEST_UPLOAD_URL)
            )

    assert TEST_FILE_NAME in data


async def test_overwrite_file_allowed(aiohttp_test_client, loop):
    upload = partial(tus.upload, file_name=TEST_FILE_NAME)

    async with aiohttp_test_client(
        upload_url=TEST_UPLOAD_URL, allow_overwrite_files=True
    ) as client:
        tus_upload_url = get_upload_url(client, TEST_UPLOAD_URL)

        with open(TEST_FILE_PATH, "rb") as handler:
            await loop.run_in_executor(None, upload, handler, tus_upload_url)

        with open(TEST_FILE_PATH, "rb") as handler:
            await loop.run_in_executor(None, upload, handler, tus_upload_url)


async def test_overwrite_file_disallowed(aiohttp_test_client, loop):
    upload = partial(tus.upload, file_name=TEST_FILE_NAME)

    async with aiohttp_test_client(
        upload_url=TEST_UPLOAD_URL, allow_overwrite_files=False
    ) as client:
        tus_upload_url = get_upload_url(client, TEST_UPLOAD_URL)

        with open(TEST_FILE_PATH, "rb") as handler:
            await loop.run_in_executor(None, upload, handler, tus_upload_url)

        with pytest.raises(tus.TusError):
            with open(TEST_FILE_PATH, "rb") as handler:
                await loop.run_in_executor(None, upload, handler, tus_upload_url)


@pytest.mark.parametrize(
    "upload_url, upload_suffix, tus_upload_url, match_info",
    (
        (TEST_UPLOAD_URL, None, TEST_UPLOAD_URL, {}),
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
    upload = partial(tus.upload, file_name=TEST_FILE_NAME)

    async with aiohttp_test_client(
        upload_url=upload_url, upload_suffix=upload_suffix
    ) as client:
        with open(TEST_FILE_PATH, "rb") as handler:
            await loop.run_in_executor(
                None, upload, handler, get_upload_url(client, tus_upload_url)
            )

        config: Config = client.app[APP_TUS_CONFIG_KEY][upload_url]
        expected_upload_path = config.resolve_upload_path(match_info) / TEST_FILE_NAME
        assert expected_upload_path.exists()
        assert expected_upload_path.read_bytes() == TEST_FILE_PATH.read_bytes()


async def test_upload_large_file(aiohttp_test_client, loop):
    upload = partial(
        tus.upload, file_name=TEST_SCREENSHOT_NAME, chunk_size=TEST_CHUNK_SIZE
    )

    async with aiohttp_test_client(upload_url=TEST_UPLOAD_URL) as client:
        with open(TEST_SCREENSHOT_PATH, "rb") as handler:
            await loop.run_in_executor(
                None, upload, handler, get_upload_url(client, TEST_UPLOAD_URL)
            )
