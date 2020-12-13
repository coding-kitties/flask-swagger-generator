from pprint import pprint
from functools import wraps


class AutoGenerateSwaggerData:
    def __init__(self):
        self.rules = []
        self.schemas = []
        self.security_schemas = []

    def __add_rule(self, name):
        rule = {
            'endpoint': name
        }
        self.rules.append(rule)

    def __add_data(self, endpoint, key, data):
        # Get rule from list by endpoint name
        rule = self.__get_rule(endpoint)
        rule[key] = data

    def __append_data(self, endpoint, key, data):
        # Get rule from list by endpoint name
        rule = self.__get_rule(endpoint)

        if key not in rule.keys():
            rule[key] = []

        rule[key].append(data)

    def __get_rule(self, endpoint):
        # TODO: build a check to ensure endpoint function names have to be unique
        # TODO: e.g. members.create and organizations.create would throw an error
        endpoint_names = []

        # Get list of endpoint names, and create endpoint if it does not exist
        for rule in self.rules:
            endpoint_names.append(rule['endpoint'])

        if endpoint not in endpoint_names:
            self.__add_rule(endpoint)

        # return rule with matching endpoint
        return next((rl for rl in self.rules if rl['endpoint'] == endpoint), None)

    def post_data(self, model):
        def swagger_post(func):

            # if post_data contains a model, add a model
            if type(model) is dict:
                self.__add_data(func.__name__, 'post_data', model)

            # if post_data contains a reference, add a reference to a schema
            if type(model) is str:
                # if model starts with "#" it refers to a schema
                if model[0] == "#":
                    self.__add_data(func.__name__, 'post_data', model)
                else:
                    # TODO: support single string inputs
                    raise Exception('Strings without # not yet supported')

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return swagger_post

    def query_parameter(self, name, input_type, required=False, description=''):
        def swagger_post(func):

            parameter_object = {
                'name': name,
                'input_type': input_type,
                'required': required,
                'description': description,
                'parameter_type': 'query'
            }

            self.__append_data(func.__name__, 'query_parameters', parameter_object)

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return swagger_post

    def response(self, code, schema, description=''):
        def swagger_post(func):

            if type(code) != int:
                raise Exception('Status code {code} should be an integer'.format(code=code))

            response_object = {
                'schema': schema,
                'code': code,
                'description': description
            }

            self.__append_data(func.__name__, 'responses', response_object)

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return swagger_post

    def security(self, reference):
        def swagger_post(func):

            self.__append_data(func.__name__, 'security', reference)

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return swagger_post

    def add_schema(self, name, schema_object):
        schema = {
            name: schema_object
        }
        self.schemas.append(schema)

    def add_security_schema(self, name, security_object):
        schema = {
            name: security_object
        }
        self.security_schemas.append(schema)
