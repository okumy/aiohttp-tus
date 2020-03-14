import attr

from aiohttp_tus.validators import check_file_name, validate_upload_metadata
from tests.common import TEST_CONFIG, TEST_DATA_PATH, TEST_UPLOAD_METADATA


def test_check_file_name():
    config = attr.evolve(TEST_CONFIG, upload_path=TEST_DATA_PATH)
    assert check_file_name(TEST_UPLOAD_METADATA, config=config) == "hello.txt"


def test_validate_upload_metadata():
    assert validate_upload_metadata(TEST_UPLOAD_METADATA) == TEST_UPLOAD_METADATA
