from pathlib import Path
from typing import Optional

from aiohttp import web

from .annotations import MappingStrBytes
from .data import Config


def check_file_name(
    valid_metadata: MappingStrBytes, *, config: Config
) -> Optional[str]:
    path = Path(valid_metadata["filename"].decode())
    if any(config.upload_path.glob(f"{path.stem}.*")):
        return path.name
    return None


def validate_upload_metadata(upload_metadata: MappingStrBytes) -> MappingStrBytes:
    if not upload_metadata.get("filename"):
        raise web.HTTPNotFound(text="Upload metadata missed filename value")
    return upload_metadata
