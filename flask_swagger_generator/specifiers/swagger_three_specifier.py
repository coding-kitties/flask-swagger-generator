import inspect
from typing import List
import re
from datetime import datetime
from marshmallow import Schema as MarshmallowSchema
from marshmallow import fields

from flask_swagger_generator.specifiers.swagger_specifier \
    import SwaggerSpecifier
from flask_swagger_generator.utils import SecurityType, InputType, RequestType
from flask_swagger_generator.specifiers.swagger_models import SwaggerModel
from flask_swagger_generator.exceptions import SwaggerGeneratorException


class SwaggerSecurity(SwaggerModel):

    def __init__(self, function_names, security_type: SecurityType):
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

    def perform_component_write(self, file):

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


class SwaggerSchema(SwaggerModel):

    def __init__(self, reference_name, schema, nested_schemas: List = None):
        super(SwaggerSchema, self).__init__()
        self.reference_name = reference_name
        self.schema = schema
        self.properties = {}

        if not nested_schemas:
            self.nested_schemas = []
        else:
            self.nested_schemas = nested_schemas

        if isinstance(schema, dict):

            for key in schema:
                self.properties[key] = "type: {}".format(
                    self.get_type(schema[key]).value
                )

        elif isinstance(schema, MarshmallowSchema):

            for field in schema.fields:

                try:
                    self.properties[field] = "type: {}".format(
                        self.get_marshmallow_type(
                            schema.fields[field]
                        ).value
                    )
                except SwaggerGeneratorException:
                    pass

    @staticmethod
    def get_marshmallow_type(value):

        if isinstance(value, fields.Integer):
            return InputType.INTEGER
        elif isinstance(value, fields.String):
            return InputType.STRING
        elif isinstance(value, fields.Float):
            return InputType.NUMBER
        elif isinstance(value, fields.List):
            return InputType.ARRAY
        elif isinstance(value, fields.Email):
            return InputType.STRING
        elif isinstance(value, fields.Boolean):
            return InputType.BOOLEAN
        elif isinstance(value, fields.DateTime):
            return InputType.DATE_TIME
        elif isinstance(value, fields.URL):
            return InputType.STRING
        else:
            raise SwaggerGeneratorException(
                "Type {} is not supported".format(type(value))
            )

    @staticmethod
    def get_type(value):

        if isinstance(value, int):
            return InputType.INTEGER
        elif isinstance(value, str):
            return InputType.STRING
        elif isinstance(value, float):
            return InputType.NUMBER
        elif isinstance(value, list):
            return InputType.ARRAY
        else:
            SwaggerGeneratorException(
                "Type {} is not supported".format(type(value))
            )

    def perform_write(self, file):

        schema_entry = inspect.cleandoc(
            """
                {}:
                  type: object
                  properties:
            """.format(self.reference_name)
        )

        schema_entry = self.indent(schema_entry, 2 * self.TAB)
        file.write(schema_entry)
        file.write('\n')

        for property_key in self.properties:
            property_entry = inspect.cleandoc(
                """
                    {}:
                      {}
                """.format(property_key, self.properties[property_key])
            )
            property_entry = self.indent(property_entry, 4 * self.TAB)
            file.write(property_entry)
            file.write('\n')


class SwaggerResponses(SwaggerModel):

    def perform_write(self, file):
        responses_entry = 'responses:'
        responses_entry = self.indent(responses_entry, 3 * self.TAB)
        file.write(responses_entry)
        file.write('\n')


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

    def perform_component_write(self, file):

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
                  $ref: '{}' 
            """.format(self.request_body_reference)
        )

        request_body_entry = self.indent(request_body_entry, 3 * self.TAB)
        file.write(request_body_entry)
        file.write('\n')

    def perform_component_write(self, file):
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


class SwaggerOperationId(SwaggerModel):

    def __init__(self, function_name):
        super(SwaggerOperationId, self).__init__()
        self.operation_id = function_name

    def perform_write(self, file):
        operation_id_entry = "operationId: '{}'".format(self.operation_id)
        operation_id_entry = self.indent(operation_id_entry, 3 * self.TAB)
        file.write(operation_id_entry)
        file.write('\n')


class SwaggerParameters(SwaggerModel):

    def perform_write(self, file):
        parameters_entry = "parameters:"
        parameters_entry = self.indent(parameters_entry, 3 * self.TAB)
        file.write(parameters_entry)
        file.write('\n')


class SwaggerTag(SwaggerModel):

    def __init__(self, group_name: str):
        super(SwaggerTag, self).__init__()
        self.group_name = group_name

    def perform_write(self, file):
        group_entry = inspect.cleandoc(
            """
                tags:
                - {}
            """.format(self.group_name)
        )

        group_entry = self.indent(group_entry, 3 * self.TAB)
        file.write(group_entry)
        file.write('\n')


class SwaggerRequestType(SwaggerModel):

    def __init__(self, function_name, request_type: RequestType):
        super(SwaggerRequestType, self).__init__()
        self.request_type = request_type
        self.function_name = function_name

    def perform_write(self, file):
        request_type_entry = "{}:".format(self.request_type.value)
        request_type_entry = self.indent(request_type_entry, 2 * self.TAB)
        file.write(request_type_entry)
        file.write('\n')


class SwaggerPathParameter(SwaggerModel):

    def __init__(
            self,
            input_type: str = None,
            name: str = None,
            description: str = None,
            required: bool = True
    ):
        super(SwaggerPathParameter, self).__init__()
        self.input_type = InputType.from_string(input_type)
        self.name = name
        self.description = description
        self.required = required

    def perform_write(self, file):
        parameter_entry = inspect.cleandoc(
            """
                - in: path
                  name: {name}
                  schema:
                    type: {input_type}
                  description: {description}
                  required: {required}
            """.format(
                name=self.name,
                required=self.required,
                description=self.description,
                input_type=self.input_type.value
            )
        )

        param = self.indent(parameter_entry, 3 * self.TAB)
        file.write(param)
        file.write("\n")


class SwaggerPath(SwaggerModel):

    def __init__(self, func_name, group, path, request_types: List[str]):
        super(SwaggerPath, self).__init__()
        self.func_name = func_name
        self.path = path
        self.group = group
        self.add_request_types(func_name, request_types)

    def add_request_types(self, function_name, request_types: List[str]):

        for request_type in request_types:

            if request_type not in ['OPTIONS', 'HEAD']:
                swagger_request_type = SwaggerRequestType(
                    function_name,
                    RequestType.from_string(request_type)
                )
                tag = SwaggerTag(self.group)
                swagger_request_type.add_swagger_model(tag)
                swagger_request_type.add_swagger_model(
                    SwaggerOperationId(function_name)
                )
                self.add_swagger_model(swagger_request_type)

    def perform_write(self, file):
        self.index_path_parameters()
        self.format_path()

        path_entry = "'{path}':".format(path=self.path)
        path = self.indent(path_entry, self.TAB)
        file.write(path)
        file.write("\n")

    def index_path_parameters(self):
        parameters = re.findall("<(.*?)>", self.path)
        swagger_request_types = self.get_swagger_child_models_of_type(
            SwaggerRequestType
        )
        parameter_models = []

        if parameters:

            for parameter in parameters:
                input_type, name = parameter.split(':')
                parameter_models.append(SwaggerPathParameter(input_type, name))

            for swagger_request_type in swagger_request_types:
                parameters = swagger_request_type\
                    .get_swagger_child_models_of_type(
                        SwaggerParameters
                )

                if not parameters:
                    parameters = SwaggerParameters()
                    swagger_request_type.add_swagger_model(parameters)

                parameters.add_swagger_models(parameter_models)

    def format_path(self):
        if len(re.findall("<(.*?)>", self.path)) > 0:

            swagger_request_types = self.get_swagger_child_models_of_type(
                SwaggerRequestType
            )

            parameters = swagger_request_types[-1]\
                .get_swagger_child_models_of_type(
                    SwaggerParameters
            )
            path_parameters = parameters[-1]\
                .get_swagger_child_models_of_type(
                    SwaggerPathParameter
            )

            for path_parameter in path_parameters:

                self.path = self.path.replace(
                    "<{}:{}>".format(
                        path_parameter.input_type.get_flask_input_type_value(),
                        path_parameter.name
                    ),
                    "{" + path_parameter.name + "}"
                )


class SwaggerThreeSpecifier(SwaggerModel, SwaggerSpecifier):

    def __init__(self):
        super().__init__()
        self.request_bodies = []
        self.schemas = []
        self.responses = []
        self.securities = []

    def perform_write(self, file):
        # Add all request bodies to request_types with same function name
        self._add_request_bodies_to_paths()
        self._add_responses_to_paths()
        self._add_securities_to_paths()

        meta = inspect.cleandoc("""
            openapi: 3.0.1
            info:
              title: {name}
              description: Generated at {time}. This is the swagger 
                ui based on the open api 3.0 specification of the {name}
              version: {version}
            externalDocs:
              description: Find out more about Swagger
              url: 'http://swagger.io'
            servers:
              - url: /
            """.format(
                name=self.application_name,
                version=self.application_version,
                time=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            )
        )

        file.write(meta)
        file.write("\n")
        file.write("paths:")
        file.write("\n")

    def write(self, file):
        """
            Overwrite the write method to add some additional functionality.
            After the perform write action the swagger specifier
            wil add the models to the bottom of the swagger definition
        """
        super().write(file)

        file.write('components:')
        file.write('\n')

        if len(self.securities) > 0:
            securities_entry = 'securitySchemes:'
            securities_entry = self.indent(securities_entry, self.TAB)
            file.write(securities_entry)
            file.write('\n')

            for security in self.securities:
                security.perform_component_write(file)

        if len(self.request_bodies) > 0:
            request_bodies_entries = 'requestBodies:'
            request_bodies_entries = self.indent(
                request_bodies_entries, self.TAB
            )
            file.write(request_bodies_entries)
            file.write('\n')

            for request_body in self.request_bodies:
                request_body.perform_component_write(file)

        if len(self.responses) > 0:
            response_entries = 'responses:'
            response_entries = self.indent(response_entries, self.TAB)
            file.write(response_entries)
            file.write('\n')

            for response in self.responses:
                response.perform_component_write(file)

        if len(self.schemas) > 0:
            schemas_entries = 'schemas:'
            schemas_entries = self.indent(schemas_entries, self.TAB)
            file.write(schemas_entries)
            file.write('\n')

            for schema in self.schemas:
                schema.perform_write(file)

    def _add_request_bodies_to_paths(self):
        swagger_paths = self.get_swagger_child_models_of_type(SwaggerPath)

        for swagger_path in swagger_paths:
            # Get the request types
            swagger_request_types = swagger_path\
                .get_swagger_child_models_of_type(
                    SwaggerRequestType
                )

            for swagger_request_type in swagger_request_types:

                for request_body in self.request_bodies:

                    if swagger_request_type.function_name \
                            == request_body.function_name:
                        swagger_request_type.add_swagger_model(request_body)

    def _add_responses_to_paths(self):
        swagger_paths = self.get_swagger_child_models_of_type(SwaggerPath)

        for swagger_path in swagger_paths:
            # Get the request types
            swagger_request_types = swagger_path \
                .get_swagger_child_models_of_type(
                    SwaggerRequestType
                )

            for swagger_request_type in swagger_request_types:

                for response in self.responses:
                    if swagger_request_type.function_name \
                            == response.function_name:

                        responses_model = swagger_request_type\
                            .get_swagger_child_models_of_type(SwaggerResponses)

                        if not responses_model:
                            responses_model = SwaggerResponses()
                            swagger_request_type.add_swagger_model(
                                responses_model
                            )

                        responses_model.add_swagger_model(response)

    def _add_securities_to_paths(self):
        swagger_paths = self.get_swagger_child_models_of_type(SwaggerPath)

        for swagger_path in swagger_paths:
            # Get the request types
            swagger_request_types = swagger_path \
                .get_swagger_child_models_of_type(
                    SwaggerRequestType
                )

            for swagger_request_type in swagger_request_types:

                for security in self.securities:
                    if swagger_request_type.function_name \
                            in security.function_names:
                        swagger_request_type.add_swagger_model(security)

    def add_endpoint(
            self,
            function_name: str,
            path: str,
            request_types: List[str],
            group: str = None
    ):

        if path == '/static/<path:filename>':
            return

        swagger_paths = self.get_swagger_child_models_of_type(SwaggerPath)

        for swagger_path in swagger_paths:

            if swagger_path.path == path:
                swagger_path.add_request_types(function_name, request_types)
                return

        new_swagger_path = SwaggerPath(
            function_name, group, path, request_types
        )
        self.add_swagger_model(new_swagger_path)

    def add_response(
            self,
            function_name: str,
            status_code: int,
            schema,
            description: str = ""
    ):
        if not isinstance(schema, SwaggerSchema):
            schema = SwaggerSchema(
                function_name + "_response_schema",
                schema
            )
            self.schemas.append(schema)

        swagger_response = SwaggerResponse(
            function_name, schema.reference_name, status_code, description,
        )

        self.responses.append(swagger_response)

    def add_query_parameters(self):
        pass

    def add_request_body(self, function_name: str, schema):

        if not isinstance(schema, SwaggerSchema):
            schema = SwaggerSchema(
                function_name + "_request_body_schema",
                schema
            )
            self.schemas.append(schema)

        swagger_request_body = SwaggerRequestBody(
            function_name, schema.reference_name
        )
        self.request_bodies.append(swagger_request_body)

    def add_security(self, function_name, security_type: SecurityType):
        for security in self.securities:

            if security.security_type.equals(security_type):
                security.function_names.append(function_name)
                return

        security_model = SwaggerSecurity([function_name], security_type)
        self.securities.append(security_model)

    def create_schema(self, reference_name, properties):
        schema = SwaggerSchema(reference_name, properties)
        self.schemas.append(schema)

        # Check if nested fields are present
        if isinstance(properties, MarshmallowSchema):

            for marshmallow_field in properties.fields:

                if isinstance(
                    properties.fields[marshmallow_field], fields.Nested
                ):
                    nested_schema = SwaggerSchema(
                        marshmallow_field,
                        properties.fields[marshmallow_field].schema
                    )
                    schema.properties[marshmallow_field] = "$ref: '#/components/schemas/{}'".format(nested_schema.reference_name)
                    self.schemas.append(nested_schema)

        return schema

    def clean(self):
        self.schemas = []
        self.securities = []
        self.responses = []
        self.swagger_models = []