import unittest

from marshmallow import ValidationError

from imgchkr_api.schemas import ValidateImageRequestSchema


class ValidateImageRequestSchemaTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._schema = ValidateImageRequestSchema()

    def test_valid_schema_passes(self) -> None:
        result = self._schema.load(
            {
                'assetPath': {
                    'location': 'location',
                    'path': 'path',
                },
                'notifications': {
                    'onStart': 'onStart',
                    'onSuccess': 'onSuccess',
                    'onFailure': 'onFailure',
                },
            }
        )
        assert result == {
            'asset_path': {
                'location': 'location',
                'path': 'path',
            },
            'notifications': {
                'on_start': 'onStart',
                'on_success': 'onSuccess',
                'on_failure': 'onFailure',
            },
        }

    def test_missing_urls_reported(self) -> None:
        with self.assertRaises(ValidationError) as exc_ctx:
            self._schema.load(
                {
                    'assetPath': {
                        'location': 'location',
                        'path': 'path',
                    },
                    'notifications': {
                        'onStart': 'onStart',
                    },
                }
            )
        assert exc_ctx.exception.messages_dict == {
            'notifications': {
                'onFailure': ['Missing data for required field.'],
                'onSuccess': ['Missing data for required field.'],
            }
        }
