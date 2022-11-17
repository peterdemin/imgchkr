from marshmallow import Schema, fields


class AssetPathSchema(Schema):
    location = fields.Str()
    path = fields.Str()


class NotificationsSchema(Schema):
    on_start = fields.URL()
    on_success = fields.URL()
    on_failure = fields.URL()


class ValidateImageRequestSchema(Schema):
    asset_path = fields.Nested(AssetPathSchema())
    notifications = fields.Nested(NotificationsSchema())
