from enum import Enum
from flask_swagger_generator.exceptions import SwaggerGeneratorException


class UrlVariableType(Enum):
    INTEGER = 'int'
    STRING = 'string'
    FLOAT = 'float'
    PATH = "path"
    UUID = "uuid"

    @staticmethod
    def from_value(value):

        if isinstance(value, UrlVariableType):
            for entry in UrlVariableType:

                if entry == value:
                    return entry

        else:
            return UrlVariableType.from_string(value)

    @staticmethod
    def from_string(value: str):

        if isinstance(value, str):

            for entry in UrlVariableType:

                if entry.value == value.lower():
                    return entry

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

    def get_swagger_url_path_variable_type(self):

        if self == UrlVariableType.STRING:
            return 'string'
        elif self == UrlVariableType.INTEGER:
            return 'integer'
        elif self == UrlVariableType.FLOAT:
            return 'number'
        elif self == UrlVariableType.PATH:
            return 'string'
        elif self == UrlVariableType.UUID:
            return 'string'

    def get_flask_url_variable_type_value(self):
        return self.value
