from enum import Enum
from flask_swagger_generator.exceptions import SwaggerGeneratorException


class SwaggerVersion(Enum):
    """
    Class SwaggerVersion: Enum for types of swagger version
    """

    VERSION_THREE = 'VERSION_THREE'
    VERSION_TWO = 'VERSION_TWO'

    @staticmethod
    def from_string(value: str):

        if isinstance(value, str):

            if value.lower() in ['three', 'version_three']:
                return SwaggerVersion.VERSION_THREE
            elif value.lower() in ['two', 'version_two']:
                return SwaggerVersion.VERSION_TWO
            else:
                raise SwaggerGeneratorException(
                    'Could not convert value {} to a swagger version'.format(
                        value
                    )
                )
        else:
            raise SwaggerGeneratorException(
                "Could not convert non string value to a swagger version"
            )

    def equals(self, other):

        if isinstance(other, Enum):
            return self.value == other.value
        else:

            try:
                data_base_type = SwaggerVersion.from_string(other)
                return data_base_type == self
            except SwaggerGeneratorException:
                pass

            return other == self.value
