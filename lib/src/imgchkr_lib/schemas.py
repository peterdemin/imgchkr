from dataclasses import dataclass

import marshmallow


@dataclass(frozen=True)
class ValidateImageRequest:
    location: str = ''
    path: str = ''
    on_start: str = ''
    on_success: str = ''
    on_failure: str = ''


class FlatValidateImageRequestSchema(marshmallow.Schema):
    location = marshmallow.fields.Str(validate=marshmallow.validate.OneOf(['local']))
    path = marshmallow.fields.Str()
    on_start = marshmallow.fields.URL(require_tld=False)
    on_success = marshmallow.fields.URL(require_tld=False)
    on_failure = marshmallow.fields.URL(require_tld=False)

    @marshmallow.post_load
    def make_control(self, data, **kwargs):
        del kwargs
        return ValidateImageRequest(**data)
