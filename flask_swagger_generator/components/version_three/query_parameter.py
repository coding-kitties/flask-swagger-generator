import inspect

from flask_swagger_generator.components.swagger_models import SwaggerModel
from flask_swagger_generator.utils import InputType


class SwaggerQueryParameter(SwaggerModel):

    def __init__(
            self,
            function_name: str = None,
            name: str = None,
            input_type: str = None,
            description: str = None,
            required: bool = False,
            allowReserved: bool = False
    ):
        super(SwaggerQueryParameter, self).__init__()
        self.function_name = function_name
        self.name = name
        self.input_type = InputType.from_string(input_type)
        self.description = description
        self.required = required
        self.allowReserved = allowReserved

    def perform_write(self, file):
        parameter_entry = inspect.cleandoc(
            """
                - in: query
                  name: {name}
                  schema:
                    type: {input_type}
                  description: {description}
                  required: {required}
                  allowReserved: {allowReserved}
            """.format(
                name=self.name,
                required=self.required,
                description=self.description,
                input_type=self.input_type.value,
                allowReserved=self.allowReserved
            )
        )

        param = self.indent(parameter_entry, 3 * self.TAB)
        file.write(param)
        file.write("\n")
