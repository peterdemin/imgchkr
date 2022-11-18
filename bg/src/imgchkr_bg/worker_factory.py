import os

import httpx
from celery import Celery

from imgchkr_bg.image_validator_factory import build_image_validator
from imgchkr_bg.tasks.health import HealthCheckTask
from imgchkr_bg.tasks.validation import ValidationTask
from imgchkr_bg.notifier import Notifier


def build_worker() -> Celery:
    celery = Celery(
        'tasks',
        broker=(os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379'),),
        backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379'),
    )
    ValidationTask(
        image_validator=build_image_validator(),
        notifier=Notifier(client=httpx.Client()),
    ).bind(celery)
    HealthCheckTask().bind(celery)
    return celery
