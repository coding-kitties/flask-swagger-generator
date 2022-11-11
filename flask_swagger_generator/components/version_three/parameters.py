from flask_swagger_generator.components.swagger_models import SwaggerModel


class SwaggerParameters(SwaggerModel):

    def perform_write(self, file):
        parameters_entry = "parameters:"
        parameters_entry = self.indent(parameters_entry, 3 * self.TAB)
        file.write(parameters_entry)
        file.write('\n')
