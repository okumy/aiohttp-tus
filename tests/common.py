from pathlib import Path

from aiohttp.test_utils import TestClient
from multidict import CIMultiDict

from aiohttp_tus.data import Config


rel = Path(__file__).parent

TEST_CHUNK_SIZE = 10240

TEST_DATA_PATH = rel / "test-data"
TEST_FILE_NAME = "hello.txt"
TEST_FILE_PATH = TEST_DATA_PATH / TEST_FILE_NAME

TEST_SCREENSHOT_NAME = "screenshot.png"
TEST_SCREENSHOT_PATH = TEST_DATA_PATH / TEST_SCREENSHOT_NAME

TEST_UPLOAD_PATH = rel / "test-uploads"
TEST_UPLOAD_URL = "/uploads"
TEST_CONFIG = Config(upload_path=TEST_UPLOAD_PATH, upload_url=TEST_UPLOAD_URL)

TEST_UPLOAD_METADATA_HEADER = "Content-Type dGV4dC9wbGFpbg==, Filename aGVsbG8udHh0"
TEST_UPLOAD_METADATA_HEADERS = CIMultiDict(
    {"Upload-Metadata": TEST_UPLOAD_METADATA_HEADER}
)
TEST_UPLOAD_METADATA = CIMultiDict(
    {"Content-Type": b"text/plain", "Filename": b"hello.txt"}
)


def get_upload_url(client: TestClient, upload_url: str) -> str:
    return f"http://{client.host}:{client.port}{upload_url}"
