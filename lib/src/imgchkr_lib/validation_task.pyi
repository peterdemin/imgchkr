import structlog

from imgchkr_lib.image_validator import ImageValidator as ImageValidator
from imgchkr_lib.notifier import Notifier as Notifier
from imgchkr_lib.validation_session import ValidationSession as ValidationSession

class ValidationTask:
    def __init__(
        self,
        image_validator: ImageValidator,
        notifier: Notifier,
        logger: structlog.stdlib.BoundLogger,
    ) -> None: ...
    def validate(self, task_id, **kwargs: str) -> dict: ...
