import pytest

from aiohttp_tus.data import get_resource_url, get_upload_url
from tests.common import TEST_CONFIG


def test_get_resource_url():
    assert get_resource_url("/uploads") == r"/uploads/{resource_uid}"


@pytest.mark.parametrize(
    "resource_url, expected",
    (
        (r"/uploads/{resource_uid}", "/uploads"),
        ("/uploads/19404e82-8008-4d64-9e97-023100c114c2", "/uploads"),
    ),
)
def test_get_upload_url(resource_url, expected):
    assert get_upload_url(resource_url) == expected


def test_upload_url_id():
    assert TEST_CONFIG.upload_url_id == "L3VwbG9hZHM_"
