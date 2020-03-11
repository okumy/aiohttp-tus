import pytest
from multidict import CIMultiDict

from aiohttp_tus.utils import parse_upload_metadata
from tests.common import TEST_UPLOAD_METADATA, TEST_UPLOAD_METADATA_HEADER


@pytest.mark.parametrize(
    "metadata_header, expected",
    (("", CIMultiDict({})), (TEST_UPLOAD_METADATA_HEADER, TEST_UPLOAD_METADATA)),
)
def test_parse_upload_metadata(metadata_header, expected):
    assert parse_upload_metadata(metadata_header) == expected
