import os

import structlog
from celery import Celery

from imgchkr_bg.tasks.health import HealthCheckTask
from imgchkr_bg.tasks.validation import CeleryValidationTask
from imgchkr_lib.validation_task_factory import build_validation_task


def build_worker() -> Celery:
    logger = structlog.stdlib.get_logger()
    celery = Celery(
        'tasks',
        broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379'),
        backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379'),
    )
    CeleryValidationTask(validation_task=build_validation_task(), celery=celery)
    HealthCheckTask(logger=logger).bind(celery)
    return celery
