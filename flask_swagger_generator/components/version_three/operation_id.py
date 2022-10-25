from flask_swagger_generator.components.swagger_models import SwaggerModel


class SwaggerOperationId(SwaggerModel):

    def __init__(self, function_name):
        super(SwaggerOperationId, self).__init__()
        self.operation_id = function_name

    def perform_write(self, file):
        operation_id_entry = "operationId: '{}'".format(self.operation_id)
        operation_id_entry = self.indent(operation_id_entry, 3 * self.TAB)
        file.write(operation_id_entry)
        file.write('\n')
