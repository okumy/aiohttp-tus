import json
import shutil
import uuid
from pathlib import Path
from typing import Any, Callable, Tuple

import attr

from .annotations import DictStrAny


@attr.dataclass(frozen=True, slots=True)
class TusConfig:
    upload_path: Path

    allow_overwrite_files: bool = False
    mkdir_mode: int = 0o755

    json_dumps: Callable[[Any], str] = json.dumps
    json_loads: Callable[[str], Any] = json.loads

    @property
    def metadata_path(self) -> Path:
        metadata_path = self.upload_path / ".metadata"
        metadata_path.mkdir(mode=self.mkdir_mode, parents=True, exist_ok=True)
        return metadata_path

    @property
    def resources_path(self) -> Path:
        resources_path = self.upload_path / ".resources"
        resources_path.mkdir(mode=self.mkdir_mode, parents=True, exist_ok=True)
        return resources_path


@attr.dataclass(frozen=True, slots=True)
class Resource:
    file_name: str
    file_size: int
    offset: int
    metadata_header: str

    uid: str = attr.Factory(lambda: str(uuid.uuid4()))

    def complete(self, *, config: TusConfig) -> Path:
        resource_path = get_resource_path(config=config, uid=self.uid)
        file_path = get_file_path(config=config, file_name=self.file_name)

        shutil.move(resource_path, file_path)
        self.delete_metadata(config=config)

        return file_path

    def delete(self, *, config: TusConfig) -> bool:
        return delete_path(get_resource_path(config=config, uid=self.uid))

    def delete_metadata(self, *, config: TusConfig) -> int:
        return delete_path(get_resource_metadata_path(config=config, uid=self.uid))

    @classmethod
    def from_metadata(cls, *, config: TusConfig, uid: str) -> "Resource":
        path = get_resource_metadata_path(config=config, uid=uid)
        data = config.json_loads(path.read_text())
        return cls(
            uid=data["uid"],
            file_name=data["file_name"],
            file_size=data["file_size"],
            offset=data["offset"],
            metadata_header=data["metadata_header"],
        )

    def save(self, *, config: TusConfig, chunk: bytes) -> Tuple[Path, int]:
        path = get_resource_path(config=config, uid=self.uid)
        with open(path, "wb+") as handler:
            handler.seek(self.offset)
            chunk_size = handler.write(chunk)
        return (path, chunk_size)

    def save_metadata(self, *, config: TusConfig) -> Tuple[Path, DictStrAny]:
        path = get_resource_metadata_path(config=config, uid=self.uid)

        data = attr.asdict(self)
        path.write_text(config.json_dumps(data))

        return (path, data)


def delete_path(path: Path) -> bool:
    if path.exists():
        path.unlink()
        return True
    return False


def get_file_path(*, config: TusConfig, file_name: str) -> Path:
    return config.upload_path / file_name


def get_resource_path(*, config: TusConfig, uid: str) -> Path:
    return config.resources_path / uid


def get_resource_metadata_path(*, config: TusConfig, uid: str) -> Path:
    return config.metadata_path / f"{uid}.json"
