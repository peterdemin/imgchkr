from typing import Tuple

from .base_location_downloader import LocationType
from .asset_downloader import AssetDownloader
from .image_header_checker import ImageHeaderChecker
from .webhook import WebhookNotifier


class ImageValidator:
    def __init__(
        self,
        asset_downloader: AssetDownloader,
        webhook_notifier: WebhookNotifier,
        header_checker: ImageHeaderChecker,
        # image_checker: ImageChecker,
    ) -> None:
        self._asset_downloader = asset_downloader
        self._webhook_notifier = webhook_notifier
        self._header_checker = header_checker
        # self._image_checker = image_checker

    def __call__(self, location_type: LocationType, path: str) -> dict:
        image_data, errors = self._download(location_type, path)
        if errors:
            return errors
        del image_data
        return {}
        # errors = self._image_checker(image_data)
        # return errors

    def _download(self, location_type: LocationType, path: str) -> Tuple[bytes, dict]:
        with self._asset_downloader(location_type, path) as asset:
            errors = asset.check_exists()
            if errors:
                return b'', errors
            _, more_errors = asset.get_size()
            errors.update(more_errors)
            header, more_errors = asset.get_header()
            errors.update(more_errors)
            if errors:
                return b'', errors
            more_errors = self._header_checker(header)
            errors.update(more_errors)
            if errors:
                return b'', errors
            image_data, more_errors = asset.get_content()
            errors.update(more_errors)
            if errors:
                return b'', errors
            # more_errors = self._image_checker(image_data)
            # errors.update(more_errors)
        if errors:
            return b'', errors
        return image_data, {}