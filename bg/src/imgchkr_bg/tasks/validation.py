from celery import Celery

from imgchkr_lib.validation_task import ValidationTask
from imgchkr_bg.constants import VALIDATE_IMAGE_TASK


class CeleryValidationTask:
    def __init__(
        self,
        validation_task: ValidationTask,
        celery: Celery,
    ) -> None:
        def bound(celery_self, **kwargs) -> dict:
            return validation_task.validate(celery_self.request.id, **kwargs)

        celery.task(name=VALIDATE_IMAGE_TASK, bind=True)(bound)
