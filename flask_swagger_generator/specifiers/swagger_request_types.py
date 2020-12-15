from enum import Enum
from flask_swagger_generator.exceptions import SwaggerGeneratorException


class SwaggerRequestType(Enum):
    """
    Class RequestType: Enum for types of requests
    """

    POST = 'POST'
    GET = 'GET'
    DELETE = 'DELETE'
    PUT = 'PUT'

    @staticmethod
    def from_string(value: str):

        if isinstance(value, str):

            if value.lower() == 'post':
                return SwaggerRequestType.POST
            elif value.lower() == 'get':
                return SwaggerRequestType.GET
            elif value.lower() == 'delete':
                return SwaggerRequestType.DELETE
            elif value.lower() == 'put':
                return SwaggerRequestType.PUT
            else:
                raise SwaggerGeneratorException(
                    'Could not convert value {} to a request type'.format(
                        value
                    )
                )

        else:
            raise SwaggerGeneratorException(
                "Could not convert non string value to a request type"
            )

    def equals(self, other):

        if isinstance(other, Enum):
            return self.value == other.value
        else:

            try:
                data_base_type = SwaggerRequestType.from_string(other)
                return data_base_type == self
            except SwaggerGeneratorException:
                pass

            return other == self.value
