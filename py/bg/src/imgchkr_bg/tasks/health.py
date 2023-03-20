import structlog
from celery import Celery

from imgchkr_bg.constants import HEALTH_TASK


class HealthCheckTask:
    def __init__(
        self,
        logger: structlog.stdlib.BoundLogger,
    ) -> None:
        self._logger = logger

    def health_check(self) -> str:
        self._logger.info("health.ok")
        return 'ok'

    def bind(self, celery: Celery) -> None:
        celery.task(name=HEALTH_TASK)(self.health_check)
