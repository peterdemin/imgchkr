from typing import Tuple

from imgchkr_lib.base_location_downloader import BaseLocationDownloader


class Asset:
    def __init__(self, downloader: BaseLocationDownloader) -> None:
        self._downloader = downloader

    def check_exists(self) -> dict:
        if not self._downloader.exists():
            return self._downloader.errors
        return {}

    def get_size(self) -> Tuple[int, dict]:
        return self._downloader.fetch_size(), self._downloader.errors

    def get_header(self) -> Tuple[bytes, dict]:
        return self._downloader.fetch_header(), self._downloader.errors

    def get_content(self) -> Tuple[bytes, dict]:
        return self._downloader.fetch_content(), self._downloader.errors
