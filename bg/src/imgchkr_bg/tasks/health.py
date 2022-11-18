from celery import Celery


class HealthCheckTask:
    def health_check(self) -> str:
        return 'ok'

    def bind(self, celery: Celery) -> None:
        celery.task(name='tasks.health')(self.health_check)
