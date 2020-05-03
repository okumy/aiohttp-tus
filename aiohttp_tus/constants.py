APP_TUS_CONFIG_KEY = "tus_config"

HEADER_CACHE_CONTROL = "Cache-Control"
HEADER_CONTENT_LENGTH = "Content-Length"
HEADER_LOCATION = "Location"
HEADER_TUS_EXTENSION = "Tus-Extension"
HEADER_TUS_FILE_EXISTS = "Tus-File-Exists"
HEADER_TUS_FILE_NAME = "Tus-File-Name"
HEADER_TUS_MAX_SIZE = "Tus-Max-Size"
HEADER_TUS_RESUMABLE = "Tus-Resumable"
HEADER_TUS_TEMP_FILENAME = "Tus-Temp-Filename"
HEADER_TUS_VERSION = "Tus-Version"
HEADER_UPLOAD_LENGTH = "Upload-Length"
HEADER_UPLOAD_METADATA = "Upload-Metadata"
HEADER_UPLOAD_OFFSET = "Upload-Offset"

TUS_API_VERSION = "1.0.0"
TUS_API_VERSION_SUPPORTED = "1.0.0"
TUS_API_EXTENSIONS = ("creation", "termination", "file-check")
TUS_MAX_FILE_SIZE = 4294967296  # 4GB

BASE_HEADERS = {
    HEADER_TUS_RESUMABLE: TUS_API_VERSION,
    HEADER_TUS_VERSION: TUS_API_VERSION_SUPPORTED,
}


# Used to get original protocol from proxy servers (nginx, apache, etc.)
HEADER_X_FORWARDED_PROTO = "X-Forwarded-Proto"
