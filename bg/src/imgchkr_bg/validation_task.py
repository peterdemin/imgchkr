from .image_validator import ImageValidator


class ValidationTask:
    def __init__(self, image_validator: ImageValidator) -> None:
        self._image_validator = image_validator

    def __call__(
        self,
        task_id: str,
        on_start: str,
        on_success: str,
        on_failure: str,
        location_type: str,
        path: str,
    ) -> None:
        image_validator = build_image_validator(
            {
                'on_start': params['on_start'],
                'on_success': params['on_success'],
                'on_failure': params['on_failure'],
            }
        )
        errors = image_validator(
            location_type=LocationType(params['location']),
            path=params['path'],
        )
        if errors:
            return {'id': self.request.id, 'state': 'failed', 'errors': errors}
        return {'id': self.request.id, 'state': 'success'}
