from typing import Dict
import httpx
from .image_header_checker import ImageHeaderChecker
from .image_validator import ImageValidator
from .asset_downloader_factory import build_asset_downloader
from .webhook import WebhookNotifier


def build_image_validator(urls: Dict[str, str]) -> ImageValidator:
    return ImageValidator(
        asset_downloader=build_asset_downloader(),
        header_checker=ImageHeaderChecker(),
        webhook_notifier=WebhookNotifier(
            client=httpx.Client(), **urls
        )
    )
