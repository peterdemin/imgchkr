import os.path

from .base_location_downloader import BaseLocationDownloader


class LocalFileReader(BaseLocationDownloader):
    def __init__(self, path: str) -> None:
        super().__init__()
        self._path = path
        self._file = None
        self._header = b''

    def __enter__(self):
        try:
            self._file = open(self._path, 'rb')
        except OSError as exc:
            self.errors['open'] = exc.args[1]
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self._file:
            self._file.close()
            self._file = None

    def exists(self) -> bool:
        return self._file is not None

    def fetch_size(self) -> int:
        try:
            size = os.path.getsize(self._path)
        except OSError as exc:
            self.errors['stat'] = exc.args[1]
            return 0
        self._check_size(size)
        return size

    def fetch_header(self) -> bytes:
        try:
            self._header = self._file.read(self._HEADER_SIZE)
        except OSError as exc:
            self.errors['read'] = exc.args[1]
        return self._header

    def fetch_content(self) -> bytes:
        try:
            return self._header + self._file.read()
        except OSError as exc:
            self.errors['read'] = exc.args[1]
        return self._header
