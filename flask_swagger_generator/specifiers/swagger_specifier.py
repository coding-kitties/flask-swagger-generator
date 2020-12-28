from abc import ABC, abstractmethod
from typing import List
from flask_swagger_generator.specifiers.swagger_request_types import \
    SwaggerRequestType
from flask_swagger_generator.utils import ParameterType, SecurityType


class SwaggerSpecifier(ABC):

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
    def add_endpoint(self, function_name, path: str, request_types: List[SwaggerRequestType]):
        raise NotImplementedError()

    @abstractmethod
    def add_parameter(
            self, function_name, parameter_type: ParameterType, name: str, schema, description, required: bool
    ):
        raise not NotImplementedError()

    @abstractmethod
    def add_query_parameters(self):
        raise NotImplementedError()

    @abstractmethod
    def add_request_body(self, function_name, schema):
        raise NotImplementedError()

    @abstractmethod
    def add_security(self, function_name, security_type: SecurityType):
        raise NotImplementedError()
