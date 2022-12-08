import contextlib
from typing import Dict, Iterator, Type

from imgchkr_lib.asset import Asset
from imgchkr_lib.base_location_downloader import BaseLocationDownloader, LocationType


class AssetDownloader:
    def __init__(self, downloaders: Dict[LocationType, Type[BaseLocationDownloader]]) -> None:
        self._downloaders = downloaders

    @contextlib.contextmanager
    def __call__(self, location_type: LocationType, path: str) -> Iterator[Asset]:
        downloader = self._downloaders[location_type]
        with downloader(path) as downloader_instance:
            yield Asset(downloader_instance)
