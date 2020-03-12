import json
import shutil
import uuid
from pathlib import Path
from typing import Any, Callable, Tuple

import attr
from aiohttp import web

from .annotations import DictStrAny


@attr.dataclass(frozen=True, slots=True)
class TusConfig:
    upload_path: Path

    allow_overwrite_files: bool = False
    mkdir_mode: int = 0o755

    json_dumps: Callable[[Any], str] = json.dumps
    json_loads: Callable[[str], Any] = json.loads

    def resolve_metadata_path(self, match_info: web.UrlMappingMatchInfo) -> Path:
        metadata_path = self.resolve_upload_path(match_info) / ".metadata"
        metadata_path.mkdir(mode=self.mkdir_mode, parents=True, exist_ok=True)
        return metadata_path

    def resolve_resources_path(self, match_info: web.UrlMappingMatchInfo) -> Path:
        resources_path = self.resolve_upload_path(match_info) / ".resources"
        resources_path.mkdir(mode=self.mkdir_mode, parents=True, exist_ok=True)
        return resources_path

    def resolve_upload_path(self, match_info: web.UrlMappingMatchInfo) -> Path:
        return Path(str(self.upload_path.absolute()).format(**match_info))


@attr.dataclass(frozen=True, slots=True)
class Resource:
    file_name: str
    file_size: int
    offset: int
    metadata_header: str

    uid: str = attr.Factory(lambda: str(uuid.uuid4()))

    def complete(
        self, *, config: TusConfig, match_info: web.UrlMappingMatchInfo
    ) -> Path:
        resource_path = get_resource_path(
            config=config, match_info=match_info, uid=self.uid
        )
        file_path = get_file_path(
            config=config, match_info=match_info, file_name=self.file_name
        )

        shutil.move(resource_path, file_path)
        self.delete_metadata(config=config, match_info=match_info)

        return file_path

    def delete(self, *, config: TusConfig, match_info: web.UrlMappingMatchInfo) -> bool:
        return delete_path(
            get_resource_path(config=config, match_info=match_info, uid=self.uid)
        )

    def delete_metadata(
        self, *, config: TusConfig, match_info: web.UrlMappingMatchInfo
    ) -> int:
        return delete_path(
            get_resource_metadata_path(
                config=config, match_info=match_info, uid=self.uid
            )
        )

    @classmethod
    def from_metadata(
        cls, *, config: TusConfig, match_info: web.UrlMappingMatchInfo
    ) -> "Resource":
        uid = match_info["resource_uid"]
        path = get_resource_metadata_path(config=config, match_info=match_info, uid=uid)
        data = config.json_loads(path.read_text())
        return cls(
            uid=data["uid"],
            file_name=data["file_name"],
            file_size=data["file_size"],
            offset=data["offset"],
            metadata_header=data["metadata_header"],
        )

    def save(
        self, *, config: TusConfig, match_info: web.UrlMappingMatchInfo, chunk: bytes
    ) -> Tuple[Path, int]:
        path = get_resource_path(config=config, match_info=match_info, uid=self.uid)
        with open(path, "wb+") as handler:
            handler.seek(self.offset)
            chunk_size = handler.write(chunk)
        return (path, chunk_size)

    def save_metadata(
        self, *, config: TusConfig, match_info: web.UrlMappingMatchInfo
    ) -> Tuple[Path, DictStrAny]:
        path = get_resource_metadata_path(
            config=config, match_info=match_info, uid=self.uid
        )

        data = attr.asdict(self)
        path.write_text(config.json_dumps(data))

        return (path, data)


def delete_path(path: Path) -> bool:
    if path.exists():
        path.unlink()
        return True
    return False


def get_file_path(
    *, config: TusConfig, match_info: web.UrlMappingMatchInfo, file_name: str
) -> Path:
    return config.resolve_upload_path(match_info) / file_name


def get_resource_path(
    *, config: TusConfig, match_info: web.UrlMappingMatchInfo, uid: str
) -> Path:
    return config.resolve_resources_path(match_info) / uid


def get_resource_metadata_path(
    *, config: TusConfig, match_info: web.UrlMappingMatchInfo, uid: str
) -> Path:
    return config.resolve_metadata_path(match_info) / f"{uid}.json"
