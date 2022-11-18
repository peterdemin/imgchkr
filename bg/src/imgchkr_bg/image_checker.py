from typing import Dict, List
from io import BytesIO
from PIL import Image


class ImageChecker:
    _MAX_SIDE = 1000

    def __call__(self, content: bytes) -> Dict[str, List[str]]:
        """Checks image bytes by loading and trying to crop it.

        Verifies that both width and height do not exceed 1000 px.

        Args:
            content: the image file contents as bytes.

        Returns:
            Errors dict (empty if no error occured).
        """
        errors = []
        with BytesIO(content) as buffer:
            try:
                with Image.open(buffer) as image:
                    width, height = image.size
                    if width > self._MAX_SIDE:
                        errors.append(f'Image width exceeds maximum ({width}/{self._MAX_SIDE})')
                    if height > self._MAX_SIDE:
                        errors.append(f'Image height exceeds maximum ({height}/{self._MAX_SIDE})')
                    image.crop((0, 0, 1, 1))
            except OSError as exc:
                errors.append(str(exc))
        if errors:
            return {'image': errors}
        return {}
