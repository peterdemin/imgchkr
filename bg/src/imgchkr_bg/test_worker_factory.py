from celery import Celery

from imgchkr_bg.worker_factory import build_worker


def test_can_build_worker():
    worker = build_worker()
    assert isinstance(worker, Celery)
