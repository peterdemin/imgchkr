from celery import Celery
from imgchkr_bg.base_location_downloader import LocationType
from imgchkr_bg.image_validator import ImageValidator
from imgchkr_bg.image_validator_factory import build_image_validator
from imgchkr_bg.schemas import FlatValidateImageRequestSchema
from imgchkr_bg.webhook import WebhookNotifier
from marshmallow import ValidationError


class ValidationTask:
    def __init__(self, image_validator: ImageValidator, webhook_notifier: WebhookNotifier) -> None:
        self._image_validator = image_validator
        self._webhook_notifier = webhook_notifier

    def validate(self, task_id, **kwargs: str) -> dict:
        schema = FlatValidateImageRequestSchema()
        try:
            params = schema.load(kwargs)
        except ValidationError as exc:
            return {'id': task_id, 'state': 'failed', 'errors': exc.messages_dict}
        image_validator = build_image_validator()
        errors = image_validator(
            location_type=LocationType(params['location']),
            path=params['path'],
        )
        if errors:
            return {'id': task_id, 'state': 'failed', 'errors': errors}
        return {'id': task_id, 'state': 'success'}

    def bind(self, celery: Celery) -> None:
        def bound_validate(celery_self, **kwargs) -> dict:
            return self.validate(celery_self.request.id, **kwargs)

        celery.task(name='tasks.validate_image', bind=True)(bound_validate)
