from enum import Enum
from flask_swagger_generator.exceptions import SwaggerGeneratorException


class InputType(Enum):
    """
    Class SwaggerVersion: Enum for types of swagger version
    """

    INTEGER = 'int'
    NUMBER = 'number'
    BOOLEAN = 'boolean'
    STRING = 'str'
    ARRAY = 'array'
    OBJECT = 'object'

    @staticmethod
    def from_string(value: str):

        if isinstance(value, str):

            if value.lower() in ['integer', 'int']:
                return InputType.INTEGER
            elif value.lower() in ['number', 'num']:
                return InputType.NUMBER
            elif value.lower() in ['boolean', 'bool']:
                return InputType.BOOLEAN
            elif value.lower() in ['string', 'str']:
                return InputType.STRING
            elif value.lower() == 'array':
                return InputType.ARRAY
            elif value.lower() == 'object':
                return InputType.OBJECT
            else:
                raise SwaggerGeneratorException(
                    'Could not convert value {} to a input type'.format(
                        value
                    )
                )
        else:
            raise SwaggerGeneratorException(
                "Could not convert non string value to a parameter type"
            )

    def equals(self, other):

        if isinstance(other, Enum):
            return self.value == other.value
        else:

            try:
                data_base_type = InputType.from_string(other)
                return data_base_type == self
            except SwaggerGeneratorException:
                pass

            return other == self.value
