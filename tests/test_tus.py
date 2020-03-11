import tempfile
from contextlib import asynccontextmanager
from pathlib import Path

import pytest
import tus
from aiohttp import web

from aiohttp_tus import setup_tus
from aiohttp_tus.constants import APP_TUS_CONFIG_KEY
from aiohttp_tus.data import TusConfig


TEST_DATA_PATH = Path(__file__).parent / "test-data"


@pytest.fixture
def aiohttp_test_client(aiohttp_client):
    @asynccontextmanager
    async def factory():
        with tempfile.TemporaryDirectory(prefix="aiohttp_tus") as temp_path:
            upload_path = Path(temp_path)
            yield await aiohttp_client(create_app(upload_path=upload_path))

    return factory


def create_app(*, upload_path: Path) -> web.Application:
    return setup_tus(web.Application(), upload_url="/uploads", upload_path=upload_path)


async def test_upload(aiohttp_test_client, loop):
    async with aiohttp_test_client() as client:
        upload_url = f"http://{client.host}:{client.port}/uploads"
        test_upload_path = TEST_DATA_PATH / "hello.txt"

        with open(test_upload_path, "rb") as handler:
            await loop.run_in_executor(None, tus.upload, handler, upload_url)

        config: TusConfig = client.app[APP_TUS_CONFIG_KEY]
        expected_upload_path = config.upload_path / "hello.txt"
        assert expected_upload_path.exists()
        assert expected_upload_path.read_bytes() == test_upload_path.read_bytes()
