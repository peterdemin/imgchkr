import unittest

from imgchkr_api.payload_validator import PayloadValidator
from imgchkr_api.utils.schema import Nested, Parameter, Schema


class PayloadValidatorTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._schema = NestedSchema()
        self._payload_validator = PayloadValidator(self._schema)

    def test_validates_sample_payload(self) -> None:
        data = self._payload_validator({'nestedParam': {'param': 'value'}})
        self.assertEqual(data, {'nested_param': {'param': 'value'}})

    def test_catches_missing_parameter(self) -> None:
        self._assert_fails(
            {'nestedParam': {}},
            {'nestedParam': {'param': ['Missing data for required field.']}},
        )

    def test_catches_empty_parameter(self) -> None:
        self._assert_fails(
            {'nestedParam': {'param': ''}},
            {'nestedParam': {'param': ['Length must be between 1 and 2048.']}},
        )

    def test_catches_long_value(self) -> None:
        self._assert_fails(
            {'nestedParam': {'param': 'X' * 10000}},
            {'nestedParam': {'param': ['Length must be between 1 and 2048.']}},
        )

    def test_catches_extra_parameter(self) -> None:
        self._assert_fails(
            {'nestedParam': {'param': 'X', 'extra': 2}},
            {'nestedParam': {'extra': ['Unknown field.']}},
        )

    def _assert_fails(self, payload: dict, errors_dict: dict) -> None:
        with self.assertRaises(self._payload_validator.Error) as exc_ctx:
            self._payload_validator(payload)
        assert exc_ctx.exception.messages_dict == errors_dict


class SampleSchema(Schema):
    param = Parameter()


class NestedSchema(Schema):
    nested_param = Nested(SampleSchema())
