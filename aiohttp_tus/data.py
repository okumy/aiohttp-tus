import base64
import json
import shutil
import uuid
from contextlib import suppress
from pathlib import Path
from typing import Awaitable, Callable, Optional, Tuple

import attr
from aiohttp import web

from .annotations import DictStrAny, JsonDumps, JsonLoads
from .constants import APP_TUS_CONFIG_KEY


@attr.dataclass(frozen=True, slots=True)
class Config:
    upload_path: Path
    upload_url: str

    upload_resource_name: Optional[str] = None

    allow_overwrite_files: bool = False
    on_upload_done: Optional["ResourceCallback"] = None

    mkdir_mode: int = 0o755

    json_dumps: JsonDumps = json.dumps
    json_loads: JsonLoads = json.loads

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

    @property
    def resource_tus_resource_name(self) -> str:
        return (
            f"tus_resource_{self.upload_url_id}"
            if self.upload_resource_name is None
            else f"{self.upload_resource_name}_resource"
        )

    @property
    def resource_tus_upload_name(self) -> str:
        return (
            f"tus_upload_{self.upload_url_id}"
            if self.upload_resource_name is None
            else self.upload_resource_name
        )

    @property
    def upload_url_id(self) -> str:
        return (
            base64.urlsafe_b64encode(self.upload_url.encode("utf-8"))
            .decode("utf-8")
            .replace("=", "_")
        )


@attr.dataclass(frozen=True, slots=True)
class Resource:
    """Dataclass to store resource metadata.

    Given dataclass used internally in between resource chunk uploads and is passed
    to ``on_upload_done`` callback if one is defined at :func:`aiohttp_tus.setup_tus`
    call.

    :param uid: Resource UUID. By default: ``str(uuid.uuid4())``
    :param file_name: Resource file name.
    :param file_size: Resource file size.
    :param offset: Current resource offset.
    :param metadata_header: Metadata header sent on initiating resource upload.
    """

    file_name: str
    file_size: int
    offset: int
    metadata_header: str

    uid: str = attr.Factory(lambda: str(uuid.uuid4()))

    def complete(self, *, config: Config, match_info: web.UrlMappingMatchInfo) -> Path:
        resource_path = get_resource_path(
            config=config, match_info=match_info, uid=self.uid
        )
        file_path = get_file_path(
            config=config, match_info=match_info, file_name=self.file_name
        )

        # Python 3.5-3.8 requires to have source as string.
        # More details: https://bugs.python.org/issue32689
        shutil.move(str(resource_path), file_path)
        self.delete_metadata(config=config, match_info=match_info)

        return file_path

    def delete(self, *, config: Config, match_info: web.UrlMappingMatchInfo) -> bool:
        return delete_path(
            get_resource_path(config=config, match_info=match_info, uid=self.uid)
        )

    def delete_metadata(
        self, *, config: Config, match_info: web.UrlMappingMatchInfo
    ) -> int:
        return delete_path(
            get_resource_metadata_path(
                config=config, match_info=match_info, uid=self.uid
            )
        )

    @classmethod
    def from_metadata(
        cls, *, config: Config, match_info: web.UrlMappingMatchInfo
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
        self, *, config: Config, match_info: web.UrlMappingMatchInfo, chunk: bytes
    ) -> Tuple[Path, int]:
        path = get_resource_path(config=config, match_info=match_info, uid=self.uid)
        with open(path, "wb+") as handler:
            handler.seek(self.offset)
            chunk_size = handler.write(chunk)
        return (path, chunk_size)

    def save_metadata(
        self, *, config: Config, match_info: web.UrlMappingMatchInfo
    ) -> Tuple[Path, DictStrAny]:
        path = get_resource_metadata_path(
            config=config, match_info=match_info, uid=self.uid
        )

        data = attr.asdict(self)
        path.write_text(config.json_dumps(data))

        return (path, data)


ResourceCallback = Callable[[web.Request, Resource, Path], Awaitable[None]]


def delete_path(path: Path) -> bool:
    if path.exists():
        path.unlink()
        return True
    return False


def get_config(request: web.Request) -> Config:
    route = request.match_info.route

    container = request.config_dict[APP_TUS_CONFIG_KEY]
    info = route.get_info()

    config_key = info.get("formatter") or info["path"]
    if config_key.endswith(r"/{resource_uid}"):
        config_key = get_upload_url(config_key)

    try:
        with suppress(KeyError):
            return container[config_key]  # type: ignore
        return container[f"{config_key}/"]  # type: ignore
    except KeyError:
        raise KeyError("Unable to find aiohttp_tus config for specified URL")


def get_file_path(
    *, config: Config, match_info: web.UrlMappingMatchInfo, file_name: str
) -> Path:
    return config.resolve_upload_path(match_info) / file_name


def get_resource_path(
    *, config: Config, match_info: web.UrlMappingMatchInfo, uid: str
) -> Path:
    return config.resolve_resources_path(match_info) / uid


def get_resource_metadata_path(
    *, config: Config, match_info: web.UrlMappingMatchInfo, uid: str
) -> Path:
    return config.resolve_metadata_path(match_info) / f"{uid}.json"


def get_resource_url(upload_url: str) -> str:
    return "/".join((upload_url.rstrip("/"), r"{resource_uid}"))


def get_upload_url(resource_url: str) -> str:
    return resource_url.rsplit("/", 1)[0]


def set_config(app: web.Application, upload_url: str, config: Config) -> None:
    if upload_url in app[APP_TUS_CONFIG_KEY]:
        raise ValueError(
            f"Upload URL {upload_url!r} already registered for the application. "
            "Please pass other `upload_url` keyword argument in `setup_tus` function."
        )
    app[APP_TUS_CONFIG_KEY][upload_url] = config
