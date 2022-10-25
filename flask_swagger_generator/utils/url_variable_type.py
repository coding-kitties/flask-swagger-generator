from enum import Enum
from flask_swagger_generator.exceptions import SwaggerGeneratorException


class UrlVariableType(Enum):
    INTEGER = 'integer'
    STRING = 'string'
    FLOAT = 'float'
    PATH = 'path'
    UUID = 'uuid'

    @staticmethod
    def from_string(value: str):

        if isinstance(value, str):

            if value.lower() == 'string':
                return UrlVariableType.STRING
            elif value.lower() == 'int':
                return UrlVariableType.INTEGER
            elif value.lower() == 'float':
                return UrlVariableType.FLOAT
            elif value.lower() == 'path':
                return UrlVariableType.PATH
            elif value.lower() == 'uuid':
                return UrlVariableType.UUID

        raise SwaggerGeneratorException(
            'Could not convert value {} to a input type'.format(
                value
            )
        )

    def equals(self, other):

        if isinstance(other, Enum):
            return self.value == other.value
        else:

            try:
                data_base_type = UrlVariableType.from_string(other)
                return data_base_type == self
            except SwaggerGeneratorException:
                pass

            return other == self.value

    def get_flask_url_variable_type_value(self):

        if self == UrlVariableType.STRING:
            return 'string'
        elif self == UrlVariableType.INTEGER:
            return 'int'
        elif self == UrlVariableType.FLOAT:
            return 'float'
        elif self == UrlVariableType.PATH:
            return 'path'
        elif self == UrlVariableType.UUID:
            return 'uuid'
