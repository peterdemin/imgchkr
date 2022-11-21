import enum
from typing import Any, Dict


class LocationType(enum.Enum):
    LOCAL_FILE = 'local'
    HTTP_URL = 'url'


class BaseLocationDownloader:
    _HEADER_SIZE = 2048
    _MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MiB

    def __init__(self, path: str) -> None:
        self.errors: Dict[str, Any] = {}
        self._path = path

    def __enter__(self) -> 'BaseLocationDownloader':
        raise NotImplementedError()

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        raise NotImplementedError()

    def exists(self) -> bool:
        raise NotImplementedError()

    def fetch_size(self) -> int:
        raise NotImplementedError()

    def fetch_header(self) -> bytes:
        raise NotImplementedError()

    def fetch_content(self) -> bytes:
        raise NotImplementedError()

    def _check_size(self, size: int) -> None:
        if size > self._MAX_CONTENT_LENGTH:
            self.errors['size'] = f'File size exceeds maximum {size}/{self._MAX_CONTENT_LENGTH}'
