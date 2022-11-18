import httpx


class Notifier:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def __call__(self, url: str, payload: dict) -> str:
        """Posts JSON payload to url.

        Args:
            url: valid URL.
            payload: JSON-compatible dict.

        Returns:
            Error message (empty on success).
        """
        if url:
            try:
                self._client.post(url, json=payload)
            except httpx.HTTPError as exc:
                return exc.args[0]
        return ''
