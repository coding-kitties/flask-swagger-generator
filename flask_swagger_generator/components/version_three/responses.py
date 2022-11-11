from flask_swagger_generator.components.swagger_models import SwaggerModel


class SwaggerResponses(SwaggerModel):

    def perform_write(self, file):
        responses_entry = 'responses:'
        responses_entry = self.indent(responses_entry, 3 * self.TAB)
        file.write(responses_entry)
        file.write('\n')
