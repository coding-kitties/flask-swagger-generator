from flask_swagger_generator.components.swagger_models import SwaggerModel
from flask_swagger_generator.utils import RequestType


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
