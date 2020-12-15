from abc import ABC, abstractmethod
from typing import List
from flask_swagger_generator.specifiers.swagger_request_types import \
    SwaggerRequestType


class SwaggerSpecifier(ABC):

    @abstractmethod
    def add_response(
            self,
            identifier: str,
            status_code: int,
            schema,
            description: str = ""
    ):
        raise NotImplementedError()

    @abstractmethod
    def add_endpoint(self, path: str, request_types: List[SwaggerRequestType]):
        raise NotImplementedError()

    @abstractmethod
    def add_query_parameters(self):
        raise NotImplementedError()

    @abstractmethod
    def add_request_body(self):
        raise NotImplementedError()

    @abstractmethod
    def add_security_schema(self):
        raise NotImplementedError()
