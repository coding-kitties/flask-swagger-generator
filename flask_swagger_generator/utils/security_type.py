from enum import Enum
from flask_swagger_generator.exceptions import SwaggerGeneratorException


class SecurityType(Enum):
    """
    Class SecurityType: Enum for types of swagger security types
    """

    BEARER_AUTH = 'BEARER_AUTH'

    @staticmethod
    def from_string(value: str):

        if isinstance(value, str):

            if value.lower() == 'bearer_auth':
                return SecurityType.BEARER_AUTH
            else:
                raise SwaggerGeneratorException(
                    'Could not convert value {} to a security type'.format(
                        value
                    )
                )
        else:
            raise SwaggerGeneratorException(
                "Could not convert non string value to a security type"
            )

    def equals(self, other):

        if isinstance(other, Enum):
            return self.value == other.value
        else:

            try:
                data_base_type = SecurityType.from_string(other)
                return data_base_type == self
            except SwaggerGeneratorException:
                pass

            return other == self.value
