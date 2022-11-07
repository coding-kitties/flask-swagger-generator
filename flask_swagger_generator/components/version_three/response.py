import inspect
from flask_swagger_generator.components.swagger_models import SwaggerModel


class SwaggerResponse(SwaggerModel):

    def __init__(
            self,
            function_name,
            schema_reference: str,
            status_code: int = 200,
            description: str = None
    ):
        super(SwaggerResponse, self).__init__()
        self.function_name = function_name
        self.description = description
        self.status_code = status_code
        self.schema_reference = schema_reference
        self.response_reference = function_name + '_response'

    def perform_write(self, file):
        response_entry = inspect.cleandoc(
            """
                '{}':
                  $ref: '#/components/responses/{}'
            """.format(self.status_code, self.response_reference)
        )
        response_entry = self.indent(response_entry, 4 * self.TAB)
        file.write(response_entry)
        file.write('\n')


class SwaggerResponseComponent(SwaggerModel):

    def __init__(
            self,
            function_name,
            schema_reference: str,
            status_code: int = 200,
            description: str = None
    ):
        super(SwaggerResponseComponent, self).__init__()
        self.function_name = function_name
        self.description = description
        self.status_code = status_code
        self.schema_reference = schema_reference
        self.response_reference = function_name + '_response'

    def perform_write(self, file):

        if self.description:
            component_entry = inspect.cleandoc(
                """
                   {}:
                     description: {}
                     content:
                        application/json:
                          schema:
                            $ref: '#/components/schemas/{}'
                """.format(
                    self.response_reference,
                    self.description,
                    self.schema_reference
                )
            )
        else:
            component_entry = inspect.cleandoc(
                """
                   {}:
                     description: {}
                     content:
                        application/json:
                            schema:
                                $ref: '#/components/schemas/{}'
                """.format(
                    self.response_reference,
                    "{} response".format(self.function_name),
                    self.schema_reference
                )
            )

        component_entry = self.indent(component_entry, 2 * self.TAB)
        file.write(component_entry)
        file.write('\n')
