class SwaggerGeneratorException(Exception):

    def __init__(self, message: str = None):
        super(SwaggerGeneratorException, self).__init__(message)
