from imgchkr_lib.validation_task_factory import build_validation_task
from imgchkr_lib.validation_task import ValidationTask


def test_can_build_worker():
    worker = build_validation_task()
    assert isinstance(worker, ValidationTask)
