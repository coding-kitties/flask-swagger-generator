import inspect
from flask_swagger_generator.components.swagger_models import SwaggerModel
from flask_swagger_generator.utils import SecurityType


class SwaggerSecurity(SwaggerModel):

    def __init__(self, function_names, security_type):
        super(SwaggerSecurity, self).__init__()
        self.security_type = security_type
        self.function_names = function_names

    def perform_write(self, file):

        if self.security_type.equals(SecurityType.BEARER_AUTH):
            security_entry = inspect.cleandoc(
                """
                    security:
                      - bearerAuth: []
                """
            )

            security_entry = self.indent(security_entry, 3 * self.TAB)
            file.write(security_entry)
            file.write('\n')


class SwaggerSecurityComponent(SwaggerModel):

    def __init__(self, function_names, security_type):
        super(SwaggerSecurityComponent, self).__init__()
        self.security_type = security_type
        self.function_names = function_names

    def perform_write(self, file):

        if SecurityType.BEARER_AUTH.equals(self.security_type):
            security_entry = inspect.cleandoc(
                """
                    bearerAuth:
                      type: http
                      scheme: bearer
                      bearerFormat: JWT
                """
            )

            security_entry = self.indent(security_entry, 2 * self.TAB)
            file.write(security_entry)
            file.write('\n')
