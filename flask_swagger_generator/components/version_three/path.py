import re

from flask_swagger_generator.components.swagger_models import SwaggerModel
from flask_swagger_generator.components.version_three.request_type \
    import SwaggerRequestType
from flask_swagger_generator.utils import RequestType
from flask_swagger_generator.components.version_three.tag import SwaggerTag
from flask_swagger_generator.components.version_three.operation_id import \
    SwaggerOperationId
from flask_swagger_generator.components.version_three.parameters import \
    SwaggerParameters
from flask_swagger_generator.components.version_three.path_parameter import \
    SwaggerPathParameter


class SwaggerPath(SwaggerModel):

    def __init__(self, func_name, group, path, request_types):
        super(SwaggerPath, self).__init__()
        self.func_name = func_name
        self.path = path
        self.group = group
        self.add_request_types(func_name, request_types)

    def add_request_types(self, function_name, request_types):

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
        self.format_path()
        path_entry = "'{path}':".format(path=self.path)
        path = self.indent(path_entry, self.TAB)
        file.write(path)
        file.write("\n")

    def format_path(self):

        if len(re.findall("<(.*?)>", self.path)) > 0:
            swagger_request_types = self.get_swagger_child_models_of_type(
                SwaggerRequestType
            )
            parameters = swagger_request_types[-1]\
                .get_swagger_child_models_of_type(
                    SwaggerParameters
            )

            if parameters:
                path_parameters = parameters[-1]\
                    .get_swagger_child_models_of_type(
                        SwaggerPathParameter
                )

                for path_parameter in path_parameters:
                    self.path = self.path.replace(
                        "<{}:{}>".format(
                            path_parameter.input_type
                            .get_flask_url_variable_type_value(),
                            path_parameter.name
                        ),
                        "{" + path_parameter.name + "}"
                    )
