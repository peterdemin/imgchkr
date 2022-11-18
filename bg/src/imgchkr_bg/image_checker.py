from io import BytesIO
from PIL import Image


class ImageChecker:

    def __call__(self, content: bytes) -> dict:
        """Checks image bytes by loading and trying to crop it.

        Args:
            content: the image file contents as bytes.

        Returns:
            Errors dict (empty if no error occured).
        """
        with BytesIO(content) as buffer:
            try:
                with Image.open(buffer) as image:
                    image.crop((0, 0, 1, 1))
                return {}
            except OSError as exc:
                return {'image': str(exc)}
