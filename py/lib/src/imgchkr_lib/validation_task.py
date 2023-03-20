import structlog

from imgchkr_lib.image_validator import ImageValidator
from imgchkr_lib.notifier import Notifier
from imgchkr_lib.validation_session import ValidationSession


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
        session = ValidationSession(
            image_validator=self._image_validator,
            notifier=self._notifier,
            logger=self._logger,
            task_id=task_id,
            kwargs=kwargs,
        )
        return session.run()
