from typing import Mapping

from marshmallow import Schema, ValidationError


class PayloadValidator:
    Error = ValidationError

    def __init__(self, schema: Schema) -> None:
        self._schema = schema

    def __call__(self, raw_data: Mapping) -> dict:
        return self._schema.load(raw_data)
