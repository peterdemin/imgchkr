import httpx

from .base_location_downloader import BaseLocationDownloader


class HTTPDownloader(BaseLocationDownloader):
    _CONTENT_LENGTH = 'Content-Length'

    def __init__(self, client: httpx.Client, url: str) -> None:
        self._client = client
        self._url = url
        self._response = None
        self._header = b''
        self.errors = {}

    def __enter__(self) -> 'HTTPDownloader':
        try:
            self._response = self._client.stream("GET", self._url)
        except IOError as exc:
            self.errors['open'] = str(exc)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self._response:
            self._response.close()
            self._response = None

    def exists(self) -> bool:
        return self._response is not None

    def fetch_size(self) -> int:
        return self._response.headers[self._CONTENT_LENGTH]

    def fetch_header(self) -> bytes:
        self._header = next(self._response.iter_bytes(self._HEADER_SIZE))
        return self._header

    def fetch_content(self) -> bytes:
        return self._header + self._response.read()
