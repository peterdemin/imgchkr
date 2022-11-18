import httpx


class WebhookNotifier:
    def __init__(
        self, on_success: str, on_failure: str, on_start: str, client: httpx.Client
    ) -> None:
        self._on_success = on_success
        self._on_failure = on_failure
        self._on_start = on_start
        self._client = client

    def on_start(self, payload: dict) -> None:
        self._client.post(self._on_start, payload)

    def on_success(self, payload: dict) -> None:
        self._client.post(self._on_success, payload)

    def on_failure(self, payload: dict) -> None:
        self._client.post(self._on_failure, payload)
