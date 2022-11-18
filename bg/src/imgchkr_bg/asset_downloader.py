import contextlib
from typing import Dict, Iterable
from .base_location_downloader import BaseLocationDownloader, LocationType
from .asset import Asset


class AssetDownloader:
    def __init__(self, downloaders: Dict[LocationType, BaseLocationDownloader]) -> None:
        self._downloaders = downloaders

    @contextlib.contextmanager
    def __call__(self, location_type: LocationType, path: str) -> Iterable[Asset]:
        downloader = self._downloaders[location_type]
        with downloader(path) as downloader_instance:
            yield Asset(downloader_instance)
