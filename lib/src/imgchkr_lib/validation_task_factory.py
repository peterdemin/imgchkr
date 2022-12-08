import httpx
import structlog
from imgchkr_lib.asset_downloader import AssetDownloader
from imgchkr_lib.base_location_downloader import LocationType
from imgchkr_lib.image_checker import ImageChecker
from imgchkr_lib.image_header_checker import ImageHeaderChecker
from imgchkr_lib.image_validator import ImageValidator
from imgchkr_lib.local_file_reader import LocalFileReader
from imgchkr_lib.notifier import Notifier
from imgchkr_lib.validation_task import ValidationTask


def build_validation_task() -> ValidationTask:
    logger = structlog.stdlib.get_logger()
    return ValidationTask(
        image_validator=ImageValidator(
            asset_downloader=AssetDownloader({LocationType.LOCAL_FILE: LocalFileReader}),
            header_checker=ImageHeaderChecker(),
            image_checker=ImageChecker(),
        ),
        notifier=Notifier(logger=logger, client=httpx.Client()),
        logger=logger,
    )
