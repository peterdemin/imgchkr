from celery import Celery
from celery.exceptions import TimeoutError as CeleryTimeoutError
from flask import Response, jsonify, Flask


class HealthEndpoint:
    def __init__(self, celery: Celery) -> None:
        self._celery = celery

    def health_check(self) -> Response:
        return jsonify("ok")

    def deep_health_check(self) -> Response:
        task = self._celery.send_task('tasks.health')
        try:
            result = task.get(timeout=5)
        except CeleryTimeoutError:
            result = 'timeout'
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
