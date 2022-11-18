import unittest
from collections import namedtuple
from unittest import mock

from celery import Celery

from imgchkr_api.validate_image_task_sender import ValidateImageTaskSender


class ValidateImageTaskSenderTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._celery = mock.Mock(spec_set=Celery)
        self._celery.send_task.return_value = namedtuple('FakeTask', 'id')('task_id')
        self._validate_image_task_sender = ValidateImageTaskSender(self._celery)

    def test_send_sample_tasks(self) -> None:
        task_id = self._validate_image_task_sender(key='value')
        assert task_id == 'task_id'
        self._celery.send_task.assert_called_once_with(
            'tasks.validate_image', kwargs={'key': 'value'}
        )
