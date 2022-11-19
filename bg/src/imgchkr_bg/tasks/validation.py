from logging import getLogger

import structlog
from celery import Celery

from imgchkr_bg.constants import VALIDATE_IMAGE_TASK
from imgchkr_bg.image_validator import ImageValidator
from imgchkr_bg.notifier import Notifier
from imgchkr_bg.validation_session import validate_image

LOGGER = getLogger(__name__)


class ValidationTask:
    def __init__(
        self,
        image_validator: ImageValidator,
        notifier: Notifier,
        logger: structlog.stdlib.BoundLogger,
    ) -> None:
        self._image_validator = image_validator
        self._notifier = notifier
        self._logger = logger

    def validate(self, task_id, **kwargs: str) -> dict:
        return validate_image(
            image_validator=self._image_validator,
            notifier=self._notifier,
            logger=self._logger,
            task_id=task_id,
            kwargs=kwargs,
        )

    def bind(self, celery: Celery) -> None:
        def bound(celery_self, **kwargs) -> dict:
            return self.validate(celery_self.request.id, **kwargs)

        celery.task(name=VALIDATE_IMAGE_TASK, bind=True)(bound)
