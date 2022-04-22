import os
from functools import wraps

from flask import Flask

from flask_swagger_generator.exceptions import SwaggerGeneratorException
from flask_swagger_generator.specifiers import SwaggerVersion, \
    SwaggerThreeSpecifier
from flask_swagger_generator.specifiers.swagger_specifier \
    import SwaggerSpecifier
from flask_swagger_generator.utils import SecurityType


class Generator:

    # Functional
    tab = "  "

    @staticmethod
    def of(version: SwaggerVersion):

        if SwaggerVersion.VERSION_THREE.equals(version):
            swagger_specifier = SwaggerThreeSpecifier()
            generator = Generator(swagger_specifier)
        else:
            raise SwaggerGeneratorException(
                "Swagger version {} is not supported".format(version)
            )
        return generator

    def __init__(self, swagger_specifier: SwaggerSpecifier):
        self._specifier = swagger_specifier
        self.destination_path = None
        self.file = None
        self.generated = False

    def generate_swagger(
            self,
            app: Flask,
            destination_path: str = None,
            application_name: str = 'Application',
            application_version: str = '1.0.0'
    ):
        self.index_endpoints(app)

        if not destination_path:
            self.destination_path = os.path.join(os.curdir, 'swagger.yaml')
        else:
            self.destination_path = destination_path

        self.specifier.set_application_name(application_name)
        self.specifier.set_application_version(application_version)
        self.file = open(destination_path, 'w')
        self.write_specification()
        self.file.close()
        self.generated = True
        self.specifier.clean()

    def write_specification(self):
        self.specifier.write(self.file)

    def response(self, status_code: int, schema, description: str = ''):

        def swagger_response(func):

            if not self.generated:
                self.specifier.add_response(
                    func.__name__, status_code, schema, description
                )

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper
        return swagger_response

    def request_body(self, schema):
        def swagger_request_body(func):

            if not self.generated:
                self.specifier.add_request_body(
                    func.__name__, schema
                )

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper
        return swagger_request_body

    def security(self, security_type: SecurityType):
        def swagger_security(func):

            if not self.generated:
                self.specifier.add_security(
                    func.__name__, security_type
                )

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper
        return swagger_security

    def create_schema(self, reference_name, properties):
        return self.specifier.create_schema(reference_name, properties)

    @property
    def specifier(self) -> SwaggerSpecifier:
        return self._specifier

    def index_endpoints(self, app):

        for rule in app.url_map.iter_rules():

            if len(rule.endpoint.split(".")) > 1:
                group, function_name = rule.endpoint.split('.')
                self.specifier.add_endpoint(
                    function_name=function_name,
                    path=str(rule),
                    request_types=rule.methods,
                    group=group
                )
            else:
                self.specifier.add_endpoint(
                    function_name=rule.endpoint,
                    path=str(rule),
                    request_types=rule.methods,
                )
