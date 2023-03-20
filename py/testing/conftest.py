import pytest


def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "--api-host", action="store", default="api", help="Override host name of API service"
    )
    parser.addoption(
        "--callback-host",
        action="store",
        default="e2e",
        help="Override host name of callback service",
    )


@pytest.fixture
def api_host(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("--api-host")


@pytest.fixture
def callback_host(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("--callback-host")
