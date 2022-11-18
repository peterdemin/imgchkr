from marshmallow import Schema as _Schema
from marshmallow import fields, validate

Nested = fields.Nested
__all__ = ('Schema', 'Parameter', 'Nested')


class Schema(_Schema):
    """Schema that uses camel-case for its external representation
    and snake-case for its internal representation.
    """

    def on_bind_field(self, field_name, field_obj):
        field_obj.data_key = camelcase(field_obj.data_key or field_name)


def camelcase(var_name):
    parts = iter(var_name.split("_"))
    return next(parts) + "".join(i.title() for i in parts)


class Parameter(fields.String):
    def __init__(self) -> None:
        super().__init__(required=True, validate=validate.Length(min=1, max=2048))
