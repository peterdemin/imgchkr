import os

import httpx
import structlog
from celery import Celery

from imgchkr_bg.asset_downloader import AssetDownloader
from imgchkr_bg.base_location_downloader import LocationType
from imgchkr_bg.image_checker import ImageChecker
from imgchkr_bg.image_header_checker import ImageHeaderChecker
from imgchkr_bg.image_validator import ImageValidator
from imgchkr_bg.local_file_reader import LocalFileReader
from imgchkr_bg.notifier import Notifier
from imgchkr_bg.tasks.health import HealthCheckTask
from imgchkr_bg.tasks.validation import ValidationTask


def build_worker() -> Celery:
    logger = structlog.stdlib.get_logger()
    celery = Celery(
        'tasks',
        broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379'),
        backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379'),
    )
    ValidationTask(
        image_validator=ImageValidator(
            asset_downloader=AssetDownloader({LocationType.LOCAL_FILE: LocalFileReader}),
            header_checker=ImageHeaderChecker(),
            image_checker=ImageChecker(),
        ),
        notifier=Notifier(logger=logger, client=httpx.Client()),
        logger=logger,
    ).bind(celery)
    HealthCheckTask(logger=logger).bind(celery)
    return celery
