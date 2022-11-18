from imgchkr_api.utils.schema import Nested, Parameter, Schema


class AssetPathSchema(Schema):
    location = Parameter()
    path = Parameter()


class NotificationsSchema(Schema):
    on_start = Parameter()
    on_success = Parameter()
    on_failure = Parameter()


class ValidateImageRequestSchema(Schema):
    asset_path = Nested(AssetPathSchema())
    notifications = Nested(NotificationsSchema())
