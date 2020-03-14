import tempfile
from functools import partial
from pathlib import Path

import tus
from aiohttp import web

from aiohttp_tus import setup_tus
from tests.common import get_upload_url, TEST_FILE_NAME, TEST_FILE_PATH


NUMBER = 5


async def test_mutltiple_tus_upload_urls(aiohttp_client, loop):
    upload = partial(tus.upload, file_name=TEST_FILE_NAME)

    with tempfile.TemporaryDirectory(prefix="aiohttp_tus") as temp_path:
        base_path = Path(temp_path)
        app = web.Application()

        for idx in range(1, NUMBER + 1):
            setup_tus(
                app, upload_path=base_path / str(idx), upload_url=f"/{idx}/uploads"
            )

        client = await aiohttp_client(app)

        for idx in range(1, NUMBER + 1):
            with open(TEST_FILE_PATH, "rb") as handler:
                await loop.run_in_executor(
                    None, upload, handler, get_upload_url(client, f"/{idx}/uploads")
                )

            expected_path = base_path / str(idx) / TEST_FILE_NAME
            assert expected_path.exists()
            assert expected_path.read_bytes() == TEST_FILE_PATH.read_bytes()
