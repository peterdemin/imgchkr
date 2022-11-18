import os

import httpx
from celery import Celery
from imgchkr_bg.schemas import FlatValidateImageRequestSchema
from marshmallow import ValidationError
from .image_validator_factory import build_image_validator
from .base_location_downloader import LocationType
from .validation_task import ValidationTask
from .webhook import WebhookNotifier

CELERY_BROKER_URL = (os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379'),)
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379')

celery = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)


def setup_celery(celery) -> None:
    # validation_task = ValidationTask(
    #     image_validator=build_image_validator(),
    #     webhook_notifier=WebhookNotifier(
    #         client=httpx.Client(), **urls
    #     ),
    # )

    # def validate_image(self, **kwargs) -> dict:
    #     return validation_task(self.request.id, **kwargs)

    celery.task(name='tasks.validate_image', bind=True)(validate_image)
    celery.task(name='tasks.health')(health_check)


def validate_image(self, **kwargs) -> dict:
    1/0
    schema = FlatValidateImageRequestSchema()
    try:
        params = schema.load(kwargs)
    except ValidationError as exc:
        return {'id': self.request.id, 'state': 'failed', 'errors': exc.messages_dict}
    image_validator = build_image_validator(
        {
            'on_start': params['on_start'],
            'on_success': params['on_success'],
            'on_failure': params['on_failure'],
        }
    )
    errors = image_validator(
        location_type=LocationType(params['location']),
        path=params['path'],
    )
    if errors:
        return {'id': self.request.id, 'state': 'failed', 'errors': errors}
    return {'id': self.request.id, 'state': 'success'}


def health_check() -> str:
    return 'ok'


setup_celery(celery)
