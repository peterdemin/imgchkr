import unittest
from typing import Callable, List
from unittest import mock

from celery import Celery

from imgchkr_lib.validation_task import ValidationTask
from imgchkr_bg.constants import VALIDATE_IMAGE_TASK
from imgchkr_bg.tasks.validation import CeleryValidationTask


class ValidationTaskTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._validation_task = mock.Mock(spec=ValidationTask)
        self._celery = mock.Mock(spec_set=Celery)
        self._registered_tasks: List[Callable] = []
        self._celery.task.return_value = self._registered_tasks.append
        self._task = CeleryValidationTask(
            validation_task=self._validation_task,
            celery=self._celery,
        )

    def test_bind_to_celery_with_request_id(self) -> None:
        self._celery.task.assert_called_once_with(name=VALIDATE_IMAGE_TASK, bind=True)
        assert len(self._registered_tasks) == 1
        task_self = mock.Mock(request=mock.Mock(id='id'))
        result = self._registered_tasks[0](task_self, key='value')
        assert result == self._validation_task.validate.return_value
        self._validation_task.validate.assert_called_once_with('id', key='value')
