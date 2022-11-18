from imgchkr_bg.asset_downloader import (
    AssetDownloader,
)
from imgchkr_bg.local_file_reader import LocalFileReader
from imgchkr_bg.base_location_downloader import LocationType


def build_asset_downloader() -> AssetDownloader:
    return AssetDownloader(
        {
            LocationType.LOCAL_FILE: LocalFileReader,
            # LocationType.HTTP_URL: HTTPDownloader,
        }
    )
