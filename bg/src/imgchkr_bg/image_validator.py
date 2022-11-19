from typing import Tuple

from imgchkr_bg.asset_downloader import AssetDownloader
from imgchkr_bg.base_location_downloader import LocationType
from imgchkr_bg.image_header_checker import ImageHeaderChecker
from imgchkr_bg.image_checker import ImageChecker


class ImageValidator:
    def __init__(
        self,
        asset_downloader: AssetDownloader,
        header_checker: ImageHeaderChecker,
        image_checker: ImageChecker,
    ) -> None:
        self._asset_downloader = asset_downloader
        self._header_checker = header_checker
        self._image_checker = image_checker

    def __call__(self, location_type: LocationType, path: str) -> dict:
        image_data, errors = self._download(location_type, path)
        return errors or self._image_checker(image_data)

    def _download(self, location_type: LocationType, path: str) -> Tuple[bytes, dict]:
        with self._asset_downloader(location_type, path) as asset:
            errors = asset.check_exists()
            if errors:
                return b'', errors
            _, errors = asset.get_size()
            header, more_errors = asset.get_header()
            errors.update(more_errors)
            if more_errors:
                return b'', errors
            more_errors = self._header_checker(header)
            errors.update(more_errors)
            if errors:
                return b'', errors
            image_data, more_errors = asset.get_content()
            errors.update(more_errors)
        if errors:
            return b'', errors
        return image_data, {}
