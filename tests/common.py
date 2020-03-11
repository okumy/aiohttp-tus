from pathlib import Path

from multidict import CIMultiDict

from aiohttp_tus.data import TusConfig


TEST_CONFIG = TusConfig(upload_path=Path(__file__).parent / "test-data")

TEST_UPLOAD_METADATA_HEADER = "Content-Type dGV4dC9wbGFpbg==, Filename aGVsbG8udHh0"
TEST_UPLOAD_METADATA_HEADERS = CIMultiDict(
    {"Upload-Metadata": TEST_UPLOAD_METADATA_HEADER}
)
TEST_UPLOAD_METADATA = CIMultiDict(
    {"Content-Type": b"text/plain", "Filename": b"hello.txt"}
)
