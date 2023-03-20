import httpx
import structlog


class Notifier:
    def __init__(
        self,
        client: httpx.Client,
        logger: structlog.stdlib.BoundLogger,
    ) -> None:
        self._client = client
        self._logger = logger

    def __call__(self, url: str, payload: dict) -> str:
        """Posts JSON payload to url.

        Args:
            url: valid URL.
            payload: JSON-compatible dict.

        Returns:
            Error message (empty on success).
        """
        log = self._logger.bind(url=url, payload=payload)
        if url:
            try:
                response = self._client.post(url, json=payload)
                response.raise_for_status()
            except httpx.HTTPError:
                log.exception("notification.failed")
                # Use generic error message for cross-platform consistency and "security"
                return 'Notification failed'
            log.info("notification.sent")
            return ''
        log.warning("notification.skipped")
        return ''
