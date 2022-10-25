from enum import Enum
from flask_swagger_generator.exceptions import SwaggerGeneratorException


class PropertyType(Enum):
    INTEGER = 'integer'
    NUMBER = 'number'
    BOOLEAN = 'boolean'
    STRING = 'string'
    ARRAY = 'array'
    OBJECT = 'object'
    NESTED = 'nested',
    DATE_TIME = 'datetime'

    @staticmethod
    def from_value(value):

        if isinstance(value, int):
            return PropertyType.INTEGER
        elif isinstance(value, str):
            return PropertyType.STRING
        elif isinstance(value, float):
            return PropertyType.NUMBER
        elif isinstance(value, list):
            return PropertyType.ARRAY
        elif isinstance(value, dict):
            return PropertyType.OBJECT
        else:
            SwaggerGeneratorException(
                "Type {} is not supported".format(type(value))
            )

    def equals(self, other):

        if isinstance(other, Enum):
            return self.value == other.value

        else:
            return PropertyType.from_value(other) == self
