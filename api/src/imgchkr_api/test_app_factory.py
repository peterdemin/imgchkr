from imgchkr_api.app_factory import build_app


def test_build_app_succeeds():
    assert build_app()
