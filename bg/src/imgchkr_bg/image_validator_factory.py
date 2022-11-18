from .image_header_checker import ImageHeaderChecker
from .image_validator import ImageValidator
from .asset_downloader_factory import build_asset_downloader


def build_image_validator() -> ImageValidator:
    return ImageValidator(
        asset_downloader=build_asset_downloader(),
        header_checker=ImageHeaderChecker(),
    )
