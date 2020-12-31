from abc import ABC, abstractmethod
from random import randint


class SwaggerModel(ABC):
    TAB = "  "

    def __init__(self):
        self.swagger_models = []

    def add_swagger_model(self, child_swagger_model):
        self.swagger_models.append(child_swagger_model)

    def add_swagger_models(self, child_swagger_models):
        self.swagger_models += child_swagger_models

    def has_swagger_model_child_type(self, child_swagger_model_type):

        for swagger_model in self.swagger_models:

            if type(swagger_model) == child_swagger_model_type:
                return True

        return False

    def get_swagger_child_models_of_type(self, swagger_model_type):
        selection = []

        for swagger_model in self.swagger_models:

            if type(swagger_model) == swagger_model_type:
                selection.append(swagger_model)

        return selection

    def write(self, file):
        self.perform_write(file)

        for swagger_model in self.swagger_models:
            swagger_model.write(file)

    @staticmethod
    def indent(string, prefix):
        return ''.join(prefix + line for line in string.splitlines(True))

    @abstractmethod
    def perform_write(self, file):
        raise NotImplementedError()

    def random_id(self):
        """
        Function to create a random ID.
        Returns: random integer that can be used as an ID
        """
        minimal = 100
        maximal = 1000000000
        rand = randint(minimal, maximal)
        return rand
