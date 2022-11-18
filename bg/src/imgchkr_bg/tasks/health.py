from celery import Celery

from imgchkr_bg.constants import HEALTH_TASK


class HealthCheckTask:
    def health_check(self) -> str:
        return 'ok'

    def bind(self, celery: Celery) -> None:
        celery.task(name=HEALTH_TASK)(self.health_check)
