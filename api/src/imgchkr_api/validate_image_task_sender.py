from celery import Celery
from imgchkr_api.task_sender_interface import TaskSenderInterface


class ValidateImageTaskSender(TaskSenderInterface):
    _NAME = 'tasks.validate_image'

    def __init__(self, celery: Celery) -> None:
        self._celery = celery

    def __call__(self, **kwargs) -> str:
        task = self._celery.send_task(self._NAME, kwargs=kwargs)
        return task.id
