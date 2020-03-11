from aiohttp_tus.validators import check_file_name, validate_upload_metadata
from tests.common import TEST_CONFIG, TEST_UPLOAD_METADATA


def test_check_file_name():
    assert check_file_name(TEST_UPLOAD_METADATA, config=TEST_CONFIG) == "hello.txt"


def test_validate_upload_metadata():
    assert validate_upload_metadata(TEST_UPLOAD_METADATA) == TEST_UPLOAD_METADATA
