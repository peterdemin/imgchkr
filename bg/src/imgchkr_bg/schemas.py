from marshmallow import Schema, fields, validate


class FlatValidateImageRequestSchema(Schema):
    location = fields.Str(validate=validate.OneOf(['local']))
    path = fields.Str()
    on_start = fields.URL()
    on_success = fields.URL()
    on_failure = fields.URL()
