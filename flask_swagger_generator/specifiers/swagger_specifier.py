from abc import ABC, abstractmethod
from typing import List
from flask_swagger_generator.utils import RequestType, SecurityType


class SwaggerSpecifier(ABC):

    def __init__(self):
        self.application_name = None
        self.application_version = None

    @abstractmethod
    def add_response(
            self,
            function_name: str,
            status_code: int,
            schema,
            description: str = ""
    ):
        raise NotImplementedError()

    @abstractmethod
    def add_endpoint(
            self,
            function_name,
            path: str,
            request_types: List[RequestType],
            group: str = None
    ):
        raise NotImplementedError()

    @abstractmethod
    def add_query_parameters(self):
        raise NotImplementedError()

    @abstractmethod
    def add_request_body(self, function_name, schema):
        raise NotImplementedError()

    @abstractmethod
    def add_security(self, function_name, security_type: SecurityType):
        raise NotImplementedError()

    def set_application_name(self, application_name):
        self.application_name = application_name

    def set_application_version(self, application_version):
        self.application_version = application_version

    @abstractmethod
    def clean(self):
        pass
