import inspect
from flask_swagger_generator.components.swagger_models import SwaggerModel


class SwaggerRequestBodyComponent(SwaggerModel):

    def __init__(
            self,
            function_name,
            schema_reference: str,
            description: str = None,
            required=True
    ):
        super(SwaggerRequestBodyComponent, self).__init__()
        self.function_name = function_name
        self.description = description
        self.required = required
        self.request_body_reference = \
            self.function_name + '_request_body'
        self.schema_reference = schema_reference

    def perform_write(self, file):
        component_entry = inspect.cleandoc(
            """
               {}:
                 description: {}
                 required: {}
                 content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/{}'
            """.format(
                self.request_body_reference,
                self.description,
                self.required,
                self.schema_reference
            )
        )

        component_entry = self.indent(component_entry, 2 * self.TAB)
        file.write(component_entry)
        file.write('\n')


class SwaggerRequestBody(SwaggerModel):

    def __init__(
            self,
            function_name,
            schema_reference: str,
            description: str = None,
            required=True
    ):
        super(SwaggerRequestBody, self).__init__()
        self.function_name = function_name
        self.description = description
        self.required = required
        self.request_body_reference = \
            self.function_name + '_request_body'
        self.schema_reference = schema_reference

    def perform_write(self, file):

        request_body_entry = inspect.cleandoc(
            """
                requestBody:
                  $ref: '#/components/requestBodies/{}' 
            """.format(self.request_body_reference)
        )

        request_body_entry = self.indent(request_body_entry, 3 * self.TAB)
        file.write(request_body_entry)
        file.write('\n')
