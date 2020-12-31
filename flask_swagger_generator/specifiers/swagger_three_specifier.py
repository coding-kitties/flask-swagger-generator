import inspect
from typing import List
import re
from datetime import datetime

from flask_swagger_generator.specifiers.swagger_specifier \
    import SwaggerSpecifier
from flask_swagger_generator.utils import SecurityType, InputType, RequestType
from flask_swagger_generator.specifiers.swagger_models import SwaggerModel


class SwaggerRequestBody(SwaggerModel):

    def __init__(self, function_name, schema):
        super(SwaggerRequestBody, self).__init__()
        self.function_name = function_name
        self.schema = schema

    def perform_write(self, file):
        reference = ""
        if isinstance(self.schema, dict):
            pass

        reference += self.random_id()

        request_body_entry = inspect.cleandoc(
            """
                request_body:
                    $ref: '{}' 
            """.format(reference)
        )

        file.write(request_body_entry)
        file.write('\n')


class SwaggerOperationId(SwaggerModel):

    def __init__(self, seed):
        super(SwaggerOperationId, self).__init__()
        self.operation_id = str(seed) + str(self.random_id())

    def perform_write(self, file):
        operation_id_entry = "operationId: {}".format(self.operation_id)
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

    def __init__(self, request_type: RequestType):
        super(SwaggerRequestType, self).__init__()
        self.request_type = request_type

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
        self.add_request_types(request_types)

    def add_request_types(self, request_types: List[str]):

        for request_type in request_types:

            if request_type not in ['OPTIONS', 'HEAD']:
                swagger_request_type = SwaggerRequestType(
                    RequestType.from_string(request_type)
                )
                tag = SwaggerTag(self.group)
                swagger_request_type.add_swagger_model(tag)
                swagger_request_type.add_swagger_model(
                    SwaggerOperationId(self.random_id())
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
                        path_parameter.input_type.value, path_parameter.name
                    ),
                    "{" + path_parameter.name + "}"
                )


class SwaggerThreeSpecifier(SwaggerModel, SwaggerSpecifier):

    def __init__(self):
        super().__init__()
        self.request_bodies = []

    def perform_write(self, file):
        meta = inspect.cleandoc("""
            openapi: 3.0.1
            info:
              title: {name}
              description: Generated at {time}. This is the swagger 
              ui based on the open api 3.0 specifiction of the {name}
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
                swagger_path.add_request_types(request_types)
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
        pass

    def add_query_parameters(self):
        pass

    def add_request_body(self, func_name, schema):
        swagger_request_body = SwaggerRequestBody(func_name, schema)
        self.request_bodies.append(swagger_request_body)

    def add_security(self, function_name, security_type: SecurityType):
        # self.security_schemas[function_name] = security_type
        pass
