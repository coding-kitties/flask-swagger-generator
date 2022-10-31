import inspect
import re
from datetime import datetime
from typing import List

from marshmallow import Schema as MarshmallowSchema

from flask_swagger_generator.components.swagger_models import SwaggerModel
from flask_swagger_generator.specifiers.swagger_specifier \
    import SwaggerSpecifier
from flask_swagger_generator.components.version_three import (
    SwaggerSchema,
    SwaggerMashmallowSchema,
    SwaggerPath,
    SwaggerRequestBody,
    SwaggerSecurity,
    SwaggerResponse,
    SwaggerParameters,
    SwaggerQueryParameter,
    SwaggerPathParameter,
    SwaggerResponses,
    SwaggerRequestType,
    SwaggerRequestBodyComponent,
    SwaggerResponseComponent,
    SwaggerSecurityComponent
)
from flask_swagger_generator.utils import SecurityType


class SwaggerThreeSpecifier(SwaggerModel, SwaggerSpecifier):

    def __init__(self):
        super().__init__()
        self.request_bodies = []
        self.request_body_components = []
        self.responses = []
        self.response_components = []
        self.securities = []
        self.security_components = []
        self.schemas = []
        self.query_parameters = []

    def perform_write(self, file):
        self._add_parameters_to_paths()
        self._add_request_bodies_to_paths()
        self._add_responses_to_paths()
        self._add_securities_to_paths()

        meta = inspect.cleandoc("""
            openapi: 3.0.1
            info:
              title: {name}
              description: Generated at {time}. This is the swagger 
                ui based on the open api 3.0 specification of the {name}
              version: {version} created by the flask swagger generator.
            externalDocs:
              description: Find out more about Swagger
              url: 'http://swagger.io'
            servers:
              - url: '{server_url}'
            """.format(
                name=self.application_name,
                version=self.application_version,
                time=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                server_url=self.server_url
            )
        )

        file.write(meta)
        file.write("\n")
        file.write("paths:")
        file.write("\n")

    def write(self, file):
        """
            Overwrite the write method to add some additional functionality.
            After the 'perform_write' action the swagger specifier
            wil add the models to the bottom of the swagger definition
        """
        super().write(file)

        file.write('components:')
        file.write('\n')

        if len(self.security_components) > 0:
            securities_entry = 'securitySchemes:'
            securities_entry = self.indent(securities_entry, self.TAB)
            file.write(securities_entry)
            file.write('\n')

            for security in self.security_components:
                security.write(file)

        if len(self.request_body_components) > 0:
            request_bodies_entries = 'requestBodies:'
            request_bodies_entries = self.indent(
                request_bodies_entries, self.TAB
            )
            file.write(request_bodies_entries)
            file.write('\n')

            for request_body in self.request_body_components:
                request_body.write(file)

        if len(self.response_components) > 0:
            response_entries = 'responses:'
            response_entries = self.indent(response_entries, self.TAB)
            file.write(response_entries)
            file.write('\n')

            for response in self.response_components:
                response.write(file)

        if len(self.schemas) > 0:
            schemas_entries = 'schemas:'
            schemas_entries = self.indent(schemas_entries, self.TAB)
            file.write(schemas_entries)
            file.write('\n')

            for schema in self.schemas:
                schema.write(file)

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

    def _add_parameters_to_paths(self):
        swagger_paths = self.get_swagger_child_models_of_type(SwaggerPath)

        for swagger_path in swagger_paths:

            swagger_request_types = swagger_path \
                .get_swagger_child_models_of_type(
                    SwaggerRequestType
                )

            parameter_models = []
            path_parameters = re.findall("<(.*?)>", swagger_path.path)

            if path_parameters:
                for path_parameter in path_parameters:
                    input_type, name = path_parameter.split(':')
                    parameter_models.append(SwaggerPathParameter(input_type, name))

            for swagger_request_type in swagger_request_types:

                for query_parameter in self.query_parameters:
                    if query_parameter.function_name \
                        == swagger_request_type.function_name:
                        parameter_models.append(query_parameter)

                if parameter_models:
                    parameters = swagger_request_type\
                        .get_swagger_child_models_of_type(
                            SwaggerParameters
                    )

                    if not parameters:
                        parameters = SwaggerParameters()
                        swagger_request_type.add_swagger_model(parameters)

                    parameters.add_swagger_models(parameter_models)

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
        schema_name = f"{function_name}_response_schema"
        schema = self._create_schema(
            schema=schema, reference_name=schema_name
        )
        response = SwaggerResponse(
            function_name, schema.reference_name, status_code, description
        )
        response_component = SwaggerResponseComponent(
            function_name, schema.reference_name, status_code, description
        )
        self.responses.append(response)
        self.response_components.append(response_component)

    def add_query_parameters(
            self,
            function_name: str,
            parameters: list
    ):

        for parameter in parameters:
            swagger_query_parameter = SwaggerQueryParameter(
                function_name, parameter.get("name"),
                parameter.get("type", "string"),
                parameter.get("description", None),
                parameter.get("required", False),
                parameter.get("allowReserved", False)
            )
            self.query_parameters.append(swagger_query_parameter)

    def add_request_body(self, function_name, schema):
        schema = self._create_schema(schema=schema, reference_name=function_name)
        request_body = SwaggerRequestBody(
            function_name, schema.reference_name
        )
        request_component_body = SwaggerRequestBodyComponent(
            function_name=function_name,
            schema_reference=schema.reference_name,
        )
        self.request_bodies.append(request_body)
        self.request_body_components.append(request_component_body)

    def add_security(self, function_name, security_type: SecurityType):
        for security in self.securities:

            if security.security_type.equals(security_type):
                security.function_names.append(function_name)
                return

        security_model = SwaggerSecurity([function_name], security_type)
        security_component = SwaggerSecurityComponent([
            function_name], security_type
        )
        self.securities.append(security_model)
        self.security_components.append(security_component)

    def _create_schema(self, schema, reference_name):
        if not isinstance(schema, SwaggerSchema) \
                and not isinstance(schema, SwaggerMashmallowSchema):

            if isinstance(schema, dict):
                schema = SwaggerSchema(
                    schema=schema, reference_name=reference_name
                )

            if isinstance(schema, MarshmallowSchema):
                schema = SwaggerMashmallowSchema(
                    schema=schema, reference_name=reference_name
                )

        self.schemas.append(schema)
        return schema

    def clean(self):
        self.request_bodies = []
        self.request_body_components = []
        self.responses = []
        self.response_components = []
        self.securities = []
        self.security_components = []
        self.schemas = []
        self.query_parameters = []
