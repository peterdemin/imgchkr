import contextlib
import os.path
from typing import BinaryIO, Iterator, Optional

from imgchkr_bg.base_location_downloader import BaseLocationDownloader


class LocalFileReader(BaseLocationDownloader):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        self._file: Optional[BinaryIO] = None
        self._header = b''

    def __enter__(self):
        with self._except_os_error('open'):
            self._file = open(self._path, 'rb')
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self._file:
            self._file.close()
            self._file = None

    def exists(self) -> bool:
        return self._file is not None

    def fetch_size(self) -> int:
        size = 0
        with self._except_os_error('read'):
            size = os.path.getsize(self._path)
            self._check_size(size)
        return size

    def fetch_header(self) -> bytes:
        assert self._file
        with self._except_os_error('read'):
            self._header = self._file.read(self._HEADER_SIZE)
        return self._header

    def fetch_content(self) -> bytes:
        assert self._file
        with self._except_os_error('read'):
            return self._header + self._file.read()
        return self._header

    @contextlib.contextmanager
    def _except_os_error(self, key: str) -> Iterator:
        try:
            yield
        except OSError as exc:
            self.errors[key] = exc.args[1]
