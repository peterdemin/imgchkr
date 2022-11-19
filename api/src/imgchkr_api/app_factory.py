import os

import structlog
from celery import Celery
from flask import Flask

from imgchkr_api.endpoints.health import HealthEndpoint
from imgchkr_api.endpoints.validate_image import ValidateImageEndpoint
from imgchkr_api.payload_validator import PayloadValidator
from imgchkr_api.receiver import ImageCheckRequestReceiver
from imgchkr_api.schemas import ValidateImageRequestSchema
from imgchkr_api.validate_image_task_sender import ValidateImageTaskSender


def build_app() -> Flask:
    logger = structlog.stdlib.get_logger()
    app = Flask(__name__)
    celery = Celery(
        'tasks',
        broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379'),
        backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379'),
    )
    ValidateImageEndpoint(
        celery=celery,
        receiver=ImageCheckRequestReceiver(
            payload_validator=PayloadValidator(schema=ValidateImageRequestSchema()),
            task_sender=ValidateImageTaskSender(celery),
        ),
        logger=logger,
    ).bind(app)
    HealthEndpoint(celery=celery, logger=logger).bind(app)
    return app
