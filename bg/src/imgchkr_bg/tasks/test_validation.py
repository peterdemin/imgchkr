import unittest
from typing import Callable, List
from unittest import mock

import structlog
from celery import Celery

from imgchkr_bg.constants import VALIDATE_IMAGE_TASK
from imgchkr_bg.image_validator import ImageValidator
from imgchkr_bg.notifier import Notifier
from imgchkr_bg.tasks.validation import ValidationTask


class ValidationTaskTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._image_validator = mock.Mock(spec=ImageValidator)
        self._notifier = mock.Mock(spec=Notifier)
        self._logger = mock.Mock(spec=structlog.stdlib.BoundLogger)
        self._task = ValidationTask(
            image_validator=self._image_validator,
            notifier=self._notifier,
            logger=self._logger,
        )
        self._celery = mock.Mock(spec_set=Celery)
        self._registered_tasks: List[Callable] = []
        self._celery.task.return_value = self._registered_tasks.append

    @mock.patch("imgchkr_bg.tasks.validation.validate_image", auto_spec=True)
    def test_bind_to_celery_with_request_id(self, validate_image: mock.Mock) -> None:
        self._task.bind(self._celery)
        self._celery.task.assert_called_once_with(name=VALIDATE_IMAGE_TASK, bind=True)
        assert len(self._registered_tasks) == 1
        task_self = mock.Mock(request=mock.Mock(id='id'))
        assert validate_image.return_value == self._registered_tasks[0](task_self, key='value')
        validate_image.assert_called_once_with(
            image_validator=self._image_validator,
            notifier=self._notifier,
            logger=self._logger,
            task_id='id',
            kwargs={'key': 'value'},
        )
