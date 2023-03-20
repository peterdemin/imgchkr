import magic


class ImageHeaderChecker:
    _JPEG_MIME_TYPE = 'image/jpeg'

    def __call__(self, header: bytes) -> dict:
        mime_type = magic.from_buffer(header, mime=True)
        if mime_type != self._JPEG_MIME_TYPE:
            return {'image': f'Not a JPEG ({mime_type})'}
        return {}
