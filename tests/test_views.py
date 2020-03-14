import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient

from aiohttp_tus import setup_tus
from tests.common import TEST_UPLOAD_PATH, TEST_UPLOAD_URL


@pytest.fixture
def tus_test_client(aiohttp_client):
    async def factory() -> TestClient:
        return await aiohttp_client(
            setup_tus(
                web.Application(),
                upload_path=TEST_UPLOAD_PATH,
                upload_url=TEST_UPLOAD_URL,
            )
        )

    return factory


async def test_start_upload(tus_test_client):
    client = await tus_test_client()
    response = await client.post(TEST_UPLOAD_URL)
    assert response.status == 500
    assert (
        await response.text()
        == "Received file upload for unsupported file transfer protocol"
    )


async def test_upload_options_200(tus_test_client):
    client = await tus_test_client()
    response = await client.options(TEST_UPLOAD_URL)
    assert response.status == 200
    assert await response.text() == ""


async def test_upload_options_204(tus_test_client):
    client = await tus_test_client()
    response = await client.options(TEST_UPLOAD_URL, headers={"Tus-Resumable": "1.0.0"})
    assert response.status == 204

    headers = response.headers
    assert headers["Tus-Resumable"] == "1.0.0"
    assert headers["Tus-Version"] == "1.0.0"
    assert headers["Tus-Extension"] == "creation,termination,file-check"
    assert headers["Tus-Max-Size"] == "4294967296"
