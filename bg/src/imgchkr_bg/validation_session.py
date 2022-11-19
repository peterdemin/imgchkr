from logging import getLogger
from typing import Any, Dict

import structlog
from marshmallow import ValidationError

from imgchkr_bg.base_location_downloader import LocationType
from imgchkr_bg.image_validator import ImageValidator
from imgchkr_bg.notifier import Notifier
from imgchkr_bg.schemas import FlatValidateImageRequestSchema, ValidateImageRequest

LOGGER = getLogger(__name__)


def validate_image(
    image_validator: ImageValidator,
    notifier: Notifier,
    logger: structlog.stdlib.BoundLogger,
    task_id: str,
    kwargs: dict,
) -> dict:
    session = _ValidationSession(
        image_validator=image_validator,
        notifier=notifier,
        logger=logger,
        task_id=task_id,
        kwargs=kwargs,
    )
    return session.run()


class _ValidationSession:  # pylint: disable=too-many-instance-attributes
    _schema = FlatValidateImageRequestSchema()
    _STARTED = 'started'
    _SUCCESS = 'success'
    _FAILED = 'failed'

    def __init__(  # pylint: disable=too-many-arguments
        self,
        image_validator: ImageValidator,
        notifier: Notifier,
        logger: structlog.stdlib.BoundLogger,
        task_id: str,
        kwargs: dict,
    ) -> None:
        self._image_validator = image_validator
        self._notifier = notifier
        self._task_id = task_id
        self._kwargs = kwargs
        self._request = ValidateImageRequest()
        self._log = logger.bind(task_id=self._task_id)
        self._pipeline = [
            self._parse_request,
            self._notify_on_start,
            self._validate_image,
            self._notify_on_success,
            self._notify_on_failure,
            self._log_result,
        ]
        self._state = self._STARTED
        self._errors: Dict[str, Any] = {}
        self._warnings: Dict[str, Any] = {}

    def run(self) -> dict:
        """Executes validation pipeline.

        All steps are always exercised.
        Each step decides if it should be executed depending on the current state.
        Order of steps is important.

        Steps:

            - parse request - populate ``self._request`` dataclass.
            - notify on start web hook.
            - validate image using :class:`.ImageValidator`.
            - notify on success web hook is state is success.
            - notify on failure web hook is state is failed.
            - log result.
        """
        for step in self._pipeline:
            step()
        return self._format_result()

    def _parse_request(self) -> None:
        self._log.info('validation.started', kwargs=self._kwargs)
        try:
            self._request = self._schema.load(self._kwargs)
        except ValidationError as exc:
            self._errors['parameters'] = exc.messages_dict
            self._state = self._FAILED

    def _notify_on_start(self) -> None:
        if self._state == self._FAILED:
            # Don't notify if parameters are invalid
            return
        notification_error = self._notifier(
            self._request.on_start, self._format_result()
        )
        if notification_error:
            self._errors['notifications'] = {'on_start': notification_error}

    def _validate_image(self) -> None:
        if self._state == self._FAILED:
            return
        errors = self._image_validator(
            location_type=LocationType(self._request.location),
            path=self._request.path,
        )
        if errors:
            self._errors.update(errors)
            self._state = self._FAILED

    def _notify_on_success(self) -> None:
        if self._state == self._FAILED:
            return
        self._state = self._SUCCESS
        notification_error = self._notifier(self._request.on_success, self._format_result())
        if notification_error:
            self._errors.setdefault('notifications', {})['on_success'] = notification_error

    def _notify_on_failure(self) -> None:
        if self._state != self._FAILED or not self._request.on_failure:
            return
        notification_error = self._notifier(self._request.on_failure, self._format_result())
        if notification_error:
            self._errors.setdefault('notifications', {})['on_failure'] = notification_error

    def _log_result(self) -> None:
        if self._state == self._SUCCESS:
            self._log.info('validation.ok')
        else:
            self._log.error('validation.failed', errors=self._errors)

    def _format_result(self) -> Dict[str, Any]:
        report: Dict[str, Any] = {
            'id': self._task_id,
            'state': self._state,
        }
        if self._errors:
            report['errors'] = self._errors
        return report
