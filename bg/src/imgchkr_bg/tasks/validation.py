from typing import Tuple

from celery import Celery
from marshmallow import ValidationError

from imgchkr_api.constants import VALIDATE_IMAGE_TASK
from imgchkr_bg.base_location_downloader import LocationType
from imgchkr_bg.image_validator import ImageValidator
from imgchkr_bg.image_validator_factory import build_image_validator
from imgchkr_bg.schemas import FlatValidateImageRequestSchema
from imgchkr_bg.webhook import WebhookNotifier


class ValidationTask:
    def __init__(self, image_validator: ImageValidator, webhook_notifier: WebhookNotifier) -> None:
        self._image_validator = image_validator
        self._webhook_notifier = webhook_notifier

    def validate(self, task_id, **kwargs: str) -> dict:
        params, errors = self._parse_params(kwargs)
        if params:
            image_validator = build_image_validator()
            errors = image_validator(
                location_type=LocationType(params['location']),
                path=params['path'],
            )
        if errors:
            return self._format_result(task_id, 'failed', errors=errors)
        return self._format_result(task_id, 'success')

    def _parse_params(self, kwargs) -> Tuple[dict, dict]:
        schema = FlatValidateImageRequestSchema()
        try:
            return schema.load(kwargs), {}
        except ValidationError as exc:
            return {}, exc.messages_dict

    def _format_result(self, task_id: str, state: str, **kwargs) -> dict:
        return {'id': task_id, 'state': state, **kwargs}

    def bind(self, celery: Celery) -> None:
        def bound_validate(celery_self, **kwargs) -> dict:
            return self.validate(celery_self.request.id, **kwargs)

        celery.task(name=VALIDATE_IMAGE_TASK, bind=True)(bound_validate)
