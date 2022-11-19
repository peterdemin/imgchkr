import structlog
from celery import Celery
from celery.exceptions import TimeoutError as CeleryTimeoutError
from flask import Flask, Response, jsonify

from imgchkr_api.constants import HEALTH_TASK


class HealthEndpoint:
    def __init__(self, celery: Celery, logger: structlog.stdlib.BoundLogger) -> None:
        self._celery = celery
        self._logger = logger

    def health_check(self) -> Response:
        self._logger.info("health.shallow", status='ok')
        return jsonify("ok")

    def deep_health_check(self) -> Response:
        task = self._celery.send_task(HEALTH_TASK)
        try:
            result = task.get(timeout=5)
        except CeleryTimeoutError:
            result = 'timeout'
        self._logger.info("health.deep", status=result)
        return jsonify({'bg': result})

    def bind(self, app: Flask) -> None:
        app.add_url_rule(
            '/health',
            endpoint='health',
            methods=['GET'],
            view_func=self.health_check,
        )
        app.add_url_rule(
            '/deep_health',
            endpoint='deep_health',
            methods=['GET'],
            view_func=self.deep_health_check,
        )
