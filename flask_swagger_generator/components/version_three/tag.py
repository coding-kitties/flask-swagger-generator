import inspect
from flask_swagger_generator.components.swagger_models import SwaggerModel


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
