from celery import Celery

from imgchkr_api.constants import VALIDATE_IMAGE_TASK
from imgchkr_api.task_sender_interface import TaskSenderInterface


class ValidateImageTaskSender(TaskSenderInterface):
    def __init__(self, celery: Celery) -> None:
        self._celery = celery

    def __call__(self, **kwargs) -> str:
        task = self._celery.send_task(VALIDATE_IMAGE_TASK, kwargs=kwargs)
        return task.id
