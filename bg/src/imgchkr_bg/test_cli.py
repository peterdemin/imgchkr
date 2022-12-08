from typing import Callable

from imgchkr_bg.cli import serve


def test_serve_imported():
    assert isinstance(serve, Callable)
