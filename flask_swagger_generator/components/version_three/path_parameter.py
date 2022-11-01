import inspect
from flask_swagger_generator.components.swagger_models import SwaggerModel
from flask_swagger_generator.utils import UrlVariableType


class SwaggerPathParameter(SwaggerModel):

    def __init__(
            self,
            input_type: str = None,
            name: str = None,
            description: str = None,
            required: bool = True
    ):
        super(SwaggerPathParameter, self).__init__()
        self.input_type = UrlVariableType.from_string(input_type)
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
                input_type=self.input_type.get_swagger_url_path_variable_type()
            )
        )

        param = self.indent(parameter_entry, 3 * self.TAB)
        file.write(param)
        file.write("\n")
