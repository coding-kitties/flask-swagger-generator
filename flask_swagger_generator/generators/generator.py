import re
import os
import inspect
from datetime import datetime
import random
from functools import wraps

from flask import Flask
from flask_swagger_generator.specifiers import SwaggerVersion, \
    SwaggerThreeSpecifier, SwaggerRequestType
from flask_swagger_generator.exceptions import SwaggerGeneratorException
from flask_swagger_generator.specifiers.swagger_specifier \
    import SwaggerSpecifier
from flask_swagger_generator.utils import ParameterType, SecurityType


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
        # # Add user added data
        # self.enrich_rules_with_additional_data(self.rules, additional_data.rules)
        # self.schemas = additional_data.schemas
        # self.security_schemas = additional_data.security_schemas
        #
        # # Format Data
        # self.get_url_params_and_format_paths(self.rules)
        # self.get_query_params(self.rules)
        # self.format_group_and_function_name(self.rules)
        # self.order_rules_by_method_and_group()
        #
        # # print('\n RULES:')
        # # pprint(self.rules)
        # #
        # # print('\n SCHEMAS:')
        # # pprint(self.schemas)
        #
        # # Write Rules to swagger file
        # self.file = open(self.get_file_path(), 'w')
        # self.write_specification()
        # self.file.close()

    def generate_swagger(
            self,
            app: Flask,
            destination_path: str,
            application_name: str = "",
            application_version: str = ""
    ):
        self.index_endpoints(app)
        self.destination_path = destination_path

    def schema(self, scheme_object):
        pass

    def response(self, status_code: int, schema, description: str = ''):

        def swagger_response(func):
            self.specifier.add_response(
                func.__name__, schema, status_code, description
            )

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper
        return swagger_response

    def parameter(
            self, parameter_type: ParameterType, name: str, description=None, required: bool = True, schema=None
    ):

        def swagger_parameter(func):
            self.specifier.add_parameter(
                func.__name__, parameter_type, name, schema, description, required
            )

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper
        return swagger_parameter

    def request_body(self, schema):
        def swagger_request_body(func):
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
            self.specifier.add_security(
                func.__name__, security_type
            )

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper
        return swagger_security

    @property
    def specifier(self) -> SwaggerSpecifier:
        return self._specifier
    #
    # @specifier.setter
    # def specifier(self, specifier: SwaggerSpecifier):
    #     self._specifier = specifier

    def get_file_path(self):
        return '{}{}{}'.format(os.getcwd(), self.relative_path, self.filename)

    def index_endpoints(self, app):
        for rule in app.url_map.iter_rules():
            function_name = rule.endpoint.split('.')[-1]
            self.specifier.add_endpoint(
                function_name=function_name,
                path=str(rule),
                request_types=self.extract_request_types(rule.methods)
            )

    def extract_request_types(self, methods):
        request_types = []

        # add supported methods to rule
        for method in methods:

            try:
                request_type = SwaggerRequestType.from_string(method)
                request_types.append(request_type.value)
            except Exception:
                pass

        return request_types

    @staticmethod
    def enrich_rules_with_additional_data(rules, additional_rule_data):
        if additional_rule_data is not None:
            # For each rule, add additional data added by users using the "swag" decorator
            for rule in rules:

                # TODO: build a check to ensure endpoint function names have to be unique
                # TODO: e.g. members.create and organizations.create would throw an error

                # get function name from blueprint
                blueprint_endpoint = rule['endpoint'].split(".")[-1]

                # if endpoint name from blueprint is also found in additional_data
                add_to_rule = next((rl for rl in additional_rule_data if rl['endpoint'] == blueprint_endpoint), None)
                if add_to_rule is not None:
                    # delete the add_to_rule data from the additional_data
                    additional_rule_data.remove(add_to_rule)

                    # remove endpoint from add_to_rule dict, to not overwrite the blueprint endpoint
                    # e.g. the blueprint's 'members.create_member' is better than the add_to_rule's 'create_member'
                    del add_to_rule['endpoint']

                    # add additional_data to rule['swag']
                    rule['swag'] = add_to_rule

    @staticmethod
    def format_group_and_function_name(rules):

        for rule in rules:
            # if rule endpoint consists of two parts e.g. groups.create_group
            if len(rule.get('endpoint').split(".")) > 1:
                group, function = rule.get('endpoint').split(".")

                rule['group'] = group.capitalize()
                rule['function'] = function

            else:
                endpoint = rule.get('endpoint')
                rule['group'] = None
                rule['function'] = endpoint

    @staticmethod
    def get_url_params_and_format_paths(rules):

        for rule in rules:

            # find path parameters in "< >"
            parameters = re.findall("<(.*?)>", rule.get('path'))

            if parameters:

                # add parameters to rule object
                rule['parameters'] = []
                for parameter in parameters:
                    # split <int:organization_id> parameter into: input_type and name
                    input_type, name = parameter.split(':')
                    parameter_object = {
                        'input_type': input_type,
                        'name': name,
                        'parameter_type': 'path'
                    }
                    rule['parameters'].append(parameter_object)

                    # format path, for example: from /<int:id>/ to /{id}/
                    rule['path'] = re.sub(
                        '<{}>'.format(parameter),
                        '{{{}}}'.format(name),
                        rule['path']
                    )

    @staticmethod
    def get_query_params(rules):
        for rule in rules:
            if 'swag' not in rule.keys():
                continue # to next loop
            if 'query_parameters' not in rule['swag'].keys():
                continue # to next loop

            # find query parameters
            parameters = rule['swag']['query_parameters']

            if parameters:
                # add parameters to rule object
                rule['parameters'] = []
                for parameter in parameters:

                    parameter_object = {
                        'input_type': parameter['input_type'],
                        'name': parameter['name'],
                        'required': parameter['required'],
                        'parameter_type': parameter['parameter_type'],
                        'description': parameter['description']

                    }
                    rule['parameters'].append(parameter_object)

    def order_rules_by_method_and_group(self):
        rules_ordered_by_method = []

        # Order by Method
        for method in self.supported_methods:
            for rule in self.rules:
                if rule.get('method') == method:
                    rules_ordered_by_method.append(rule)

        rules_with_group = []
        rules_without_group = []

        # Routes are grouped by path to ensure rules are associated with correct paths
        # Unfortunately this ruins a neat ordering by method, but is necessary:
        # Swagger does not support duplicate path entries

        # Not supported: Route Group( path_A[GET] path_B[GET] path_A[POST] path_B[POST] )
        # Supported: Route Group( path_A[GET, POST] path_B[GET, POST] )
        rules_ordered_by_path = sorted(rules_ordered_by_method, key=lambda s_rule: s_rule.get('path'))

        # Order by Group
        for rule in rules_ordered_by_path:
            if rule.get('group') is None:
                rules_without_group.append(rule)
            else:
                rules_with_group.append(rule)

        rules_sorted_by_group = sorted(rules_with_group, key=lambda s_rule: s_rule.get('group'))
        all_rules_sorted = rules_sorted_by_group + rules_without_group
        self.rules = all_rules_sorted

    def get_method(self, methods):

        # add supported methods to rule
        for supported_method in self.supported_methods:

            if supported_method in methods:
                return supported_method

        raise Exception('HTTP method not supported by auto generator')

    @staticmethod
    def indent(string, prefix):
        return ''.join(prefix + line for line in string.splitlines(True))

    def write_specification(self):
        self.write_meta()
        self.write_paths()
        self.write_components()

    def write_meta(self):
        meta = inspect.cleandoc("""
            openapi: 3.0.1
            info:
              title: {name}
              description: Generated at {time}. This is the swagger ui based on the open api 3.0 specifiction of the {name}
              version: {version}
            externalDocs:
              description: Find out more about Swagger
              url: 'http://swagger.io'
            servers:
              - url: /
            """.format(
                name=self.app_name,
                version=self.version,
                time=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            )
        )

        self.file.write(meta)
        self.file.write("\n")

    def write_paths(self):
        self.file.write("paths:")
        self.file.write("\n")

        headers = []
        paths = []
        for rule in self.rules:

            group = rule.get('group')
            if group not in headers:
                if group == None:
                    headers.append(None)
                    self.add_header("Other Paths")
                else:
                    headers.append(group)
                    self.add_header(group)

            path = rule.get('path')
            if path not in paths:
                paths.append(path)
                self.add_path(path)

            self.write_rule(rule)
            # rules_with_same_path = self.find_object_by_key_value_in_list(self.rules, "path", path)
            # for rule_with_same_path in rules_with_same_path:
            #     self.write_rule(rule_with_same_path)
            #     # delete rule to prevent double writing
            #     del rule_with_same_path

    @staticmethod
    def find_object_by_key_value_in_list(list_with_objects, key, value):
        return [x for x in list_with_objects if x[key] == value]

    @staticmethod
    def find_object_by_key_in_list(list_with_objects, key):
        return [x for x in list_with_objects if x == key]

    def add_header(self, header_title):
        header = inspect.cleandoc("""
              #-------------------------------
              # {header_title} related paths
              #-------------------------------
        """.format(header_title=header_title.capitalize()))

        header = self.indent(header, self.tab)
        self.file.write(header)
        self.file.write("\n")

    def add_path(self, path):
        path = inspect.cleandoc("""
            '{path}':
        """.format(path=path))

        path = self.indent(path, self.tab)
        self.file.write(path)
        self.file.write("\n")

    def write_rule(self, rule):
        self.write_rule_meta(rule, 2)
        if rule.get('parameters'):
            self.write_parameters(rule.get('parameters'), 3)

        self.write_request_body(rule, 3)
        self.write_responses(rule, 3)
        self.write_security(rule, 3)

        self.file.write("\n")

    def write_rule_meta(self, rule, tabs):
        rule_meta = inspect.cleandoc("""
            {method}:
              tags:
                - {group}
              summary: {function}
              operationId: '{function}{random}'
        """.format(
                method=rule.get('method').lower(),
                random=random.randint(0, 10000),
                group=rule.get('group', ''),
                function=rule.get('function')
            )
        )

        rule_meta = self.indent(rule_meta, self.tab * tabs)
        self.file.write(rule_meta)
        self.file.write("\n")

    def write_parameters(self, parameters, tabs):
        param = inspect.cleandoc("""
            parameters:
        """)

        param = self.indent(param, self.tab * tabs)
        self.file.write(param)
        self.file.write("\n")

        for parameter in parameters:
            self.write_parameter(parameter, tabs + 1)

    @staticmethod
    def format_parameter_type(input_type):
        if input_type in {'int', 'integer', int}:
            return 'integer'
        if input_type in {'str', 'string', str}:
            return 'string'
        if input_type in {'object', 'dict', 'dictionary', dict}:
            return 'object'
        if input_type in {'list', list}:
            return 'array'
        if input_type == 'path':
            return 'string'

        raise Exception('Parameter type {} not supported'.format(input_type))

    def write_parameter(self, parameter, tabs):
        parameter['input_type'] = self.format_parameter_type(parameter['input_type'])

        name = parameter.get('name')
        required = True
        description = name
        if 'required' in parameter:
            required = parameter.get('required')
        if 'description' in parameter:
            description = parameter.get('description')

        parameter = inspect.cleandoc("""
            - in: {parameter_type}
              name: {name}
              schema:
                type: {input_type}
              description: {description}
              required: {required}
            """.format(
                name=name,
                required=required,
                description=description,
                parameter_type=parameter.get('parameter_type'),
                input_type=parameter.get('input_type'),
            )
        )

        parameter = self.indent(parameter, self.tab * tabs)
        self.file.write(parameter)
        self.file.write("\n")

    def write_request_body(self, rule, tabs):
        # if user did not add any data, request body cannot be generated
        if 'swag' not in rule:
            return None

        if "post_data" in rule['swag']:
            post_data = rule['swag']['post_data']
            post_data_type = type(post_data)

            # Post Data is string
            if post_data_type is str:

                # post_data_type is a string, and refers to a schema
                if post_data[0] == "#":
                    # exclude the "#" from the reference
                    self.check_if_schema_exists(post_data)

                    reference = post_data[1:]
                    request_body = inspect.cleandoc("""
                        requestBody:
                          $ref: '#/components/requestBodies/{reference}Body'
                    """).format(reference=reference)

                # post_data_type is a string, but does not refer to a schema
                else:
                    # TODO add support for string
                    request_body = self.standard_request_body()

            # Post Data is dict
            elif post_data_type is dict:

                # Function name
                func_name = rule['function']

                # Generate unique name based on function, create_member to CreateMember
                schema_name = self.create_name_from_function(func_name)

                # Check if name already exists
                duplicate_name = [x for x in self.schemas if list((x.keys()))[0] == schema_name]
                if duplicate_name:
                    raise Exception('Tried to generate schema {name} based on function name {func}, '
                                    'but schema already exists'.format(name=schema_name, func=func_name))

                # refer to yet to be built schema
                request_body = inspect.cleandoc("""
                                        requestBody:
                                          $ref: '#/components/requestBodies/{reference}Body'
                                    """).format(reference=schema_name)

                # ensure schema will be built
                self.schemas.append({schema_name: post_data})

            # Write the request body
            request_body = self.indent(request_body, self.tab * tabs)
            self.file.write(request_body)
            self.file.write("\n")
        else:
            pass

    @staticmethod
    def create_name_from_function(func_name):
        words = func_name.split("_")
        capitalized_words = [x.capitalize() for x in words]
        return ''.join(capitalized_words)

    @staticmethod
    def standard_request_body():
        return inspect.cleandoc("""
                requestBody:
                  content: 
                    text/plain:
                      schema:
                        type: string
            """)

    def write_responses(self, rule, tabs):
        if 'swag' not in rule.keys():
            return
        if 'responses' not in rule['swag'].keys():
            return

        responses = rule['swag']['responses']

        param = inspect.cleandoc("""
            responses:
        """)

        param = self.indent(param, self.tab * tabs)
        self.file.write(param)
        self.file.write("\n")

        for response in responses:
            self.write_response(rule, response, tabs + 1)

    def write_response(self, rule, response, tabs):

        schema = response['schema']
        schema_name = None

        if type(schema) is dict:
            # Generate unique name based on function, create_member to CreateMember
            schema_name = self.create_name_from_function(rule['function']) + 'Response'
            # Ensure schema will be generated
            self.schemas.append({schema_name: schema})
        else:
            # A #reference to a schema, remove the '#' at the beginning
            self.check_if_schema_exists(schema)
            schema_name = schema[1:]

        parameter = inspect.cleandoc("""
            '{code}':
              description: {description}
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/{schema_name}'
        """.format(code=response['code'], description=response['description'], schema_name=schema_name))

        parameter = self.indent(parameter, self.tab * tabs)
        self.file.write(parameter)
        self.file.write("\n")

    def write_security(self, rule, tabs):
        if 'swag' not in rule:
            return
        if 'security' not in rule['swag']:
            return

        security = inspect.cleandoc("""security:""")
        security = self.indent(security, self.tab * tabs)
        self.file.write(security)
        self.file.write("\n")

        security_references = rule['swag']['security']
        for reference in security_references:
            self.write_security_reference(reference, tabs + 1)

    def write_security_reference(self, reference, tabs):
        if reference[0] == '#':
            reference = reference[1:]

        security = inspect.cleandoc("""
            - {ref}: []
        """.format(ref=reference))

        security = self.indent(security, self.tab * tabs)
        self.file.write(security)
        self.file.write("\n")

    def write_components(self):
        components = inspect.cleandoc("""
                    components:
                """)
        self.file.write(components)
        self.file.write("\n")

        self.write_security_schemas(1)
        self.write_reusable_request_bodies(1)
        self.write_schemas(1)

    def write_security_schemas(self, tabs):
        sec_schemas = inspect.cleandoc("""
                                            securitySchemes:
                                        """)
        sec_schemas = self.indent(sec_schemas, self.tab * tabs)
        self.file.write(sec_schemas)
        self.file.write("\n")

        # create standard request bodies for all schemas
        for schema in self.security_schemas:
            self.write_security_schema(schema, tabs + 1)

    def write_security_schema(self, schema, tabs):
        name = self.gk(schema)
        schemas = inspect.cleandoc("""
                    {name}:
                    """.format(name=name))
        schemas = self.indent(schemas, self.tab * tabs)
        self.file.write(schemas)
        self.file.write("\n")

        values = schema[name]
        for key in values:
            self.write_security_parameter(key, values[key], tabs + 1)

        self.file.write("\n")

    def write_security_parameter(self, key, value, tabs):
        parameter = inspect.cleandoc("""
                            {key}: {value}
                            """.format(key=key, value=value))
        parameter = self.indent(parameter, self.tab * tabs)
        self.file.write(parameter)
        self.file.write("\n")

    def write_reusable_request_bodies(self, tabs):
        responses = inspect.cleandoc("""
                                    requestBodies:
                                """)
        responses = self.indent(responses, self.tab * tabs)
        self.file.write(responses)
        self.file.write("\n")

        # create standard request bodies for all schemas
        for schema in self.schemas:
            self.write_reusable_request_body(schema, tabs + 1)

        # for rule in self.rules:
        #
        #     # check if user added manual data
        #     if 'swag' in rule:
        #
        #         # if a rule has post_data
        #         if 'post_data' in rule['swag']:
        #
        #             post_data = rule['swag']['post_data']
        #
        #             # if the post_data is a string
        #             if type(post_data) is str:
        #
        #                 # if the post_data is a reference, denoted by "#" at the beginning
        #                 if post_data[0] == "#":
        #
        #                     # Get the reference without the "#" at the beginning
        #                     reference = post_data[1:]
        #                     match = None
        #
        #                     # check if reference exists in schemas
        #                     for schema in self.schemas:
        #
        #                         # get key of schema object
        #                         key = list(schema.keys())[0]
        #
        #                         # check if key is equal to reference
        #                         if key == reference:
        #                             match = schema
        #                             break
        #
        #                     if match:
        #                         # create reusable request body referencing to schema
        #                         self.write_reusable_request_body(match, tabs + 1)
        #                     else:
        #                         raise Exception("Reference {ref} is not defined in schemas".
        #                                            format(ref=post_data))

    def write_reusable_request_body(self, schema, tabs):
        name = self.gk(schema)
        values = self.format_values(schema)
        schemas = inspect.cleandoc("""
            {name}Body:
              description: A JSON object containing{values}
              required: true
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/{name}'
            """.format(
            name=name, values=values
        ))

        schemas = self.indent(schemas, self.tab * tabs)
        self.file.write(schemas)
        self.file.write("\n")

    @staticmethod
    def gk(schema):
        # get key from schema
        return list(schema.keys())[0]

    def gv(self, schema):
        # get values from schema
        name = self.gk(schema)
        return list(schema[name].keys())

    def format_values(self, schema):
        schema_key = self.gk(schema)
        values = schema[schema_key]
        keys = values.keys()
        string = ''
        # format schema values as " name (type)"
        for key in keys:
            value_type = type(values[key]).__name__
            string = string + ", {key} ({type})".format(key=key, type=value_type)

        return string

    def write_schemas(self, tabs):

        schemas = inspect.cleandoc("""
                            schemas:
                        """)
        schemas = self.indent(schemas, self.tab * tabs)
        self.file.write(schemas)
        self.file.write("\n")

        for schema in self.schemas:
            self.write_schema(schema, tabs + 1)

    def write_schema(self, schema, tabs):
        # Get the key of the schema
        key = list(schema.keys())[0]
        values = schema[key]
        self.write_schema_values(key, values, tabs)

    def write_schema_values(self, key, values, tabs):
        # Determine schema type
        schema_type = self.format_parameter_type(type(values))

        if schema_type == 'array':
            self.write_array_values(key, values, tabs)
            return

        schema = inspect.cleandoc("""
                    {name}:
                      type: {type}
                      properties: 
                """).format(name=key, type=schema_type)

        schema = self.indent(schema, self.tab * tabs)
        self.file.write(schema)
        self.file.write("\n")

        for name in values:
            self.write_schema_variable(name, values[name], tabs + 2)

    def write_array_values(self, key, values, tabs):
        # Determine schema type
        schema_type = self.format_parameter_type(type(values))

        schema = inspect.cleandoc("""
           {name}:
             type: {type}
             items: 
       """).format(name=key, type=schema_type)

        schema = self.indent(schema, self.tab * tabs)
        self.file.write(schema)
        self.file.write("\n")

        for value in values:
            self.write_array_variable(value, value, tabs + 2)

    def write_schema_variable(self, name, example, tabs):
        var_type = type(example)
        key = 'example'
        recursive = False
        if var_type == str:
            if example[0] == '#':
                # if example is a #reference to another schema, create a reference
                self.check_if_schema_exists(example)  # check if schema exists
                var_type = dict  # set var_type to dict
                key = '$ref'  # change 'example' key to 'ref'
                example = "'#/components/schemas/{schema}'".format(schema=example[1:])  # refer to correct schema

                # For references in an array, the name will be #Reference, this has to be changed into Reference
                if name[0] == '#':
                    name = name[1:]
            else:
                # if no reference, regular string
                example = '\"{0}\"'.format(example)
        elif var_type in {dict, list}:
            # Schema contains recursive object or list, write it
            self.write_schema_values(name, example, tabs)
            return

        formatted_var_type = self.format_parameter_type(var_type)

        variable = inspect.cleandoc("""
                            {name}: 
                              type: {type}
                              {key}: {example}
                        """).format(name=name, type=formatted_var_type, example=example, key=key)

        variable = self.indent(variable, self.tab * tabs)
        self.file.write(variable)
        self.file.write("\n")

    def write_array_variable(self, name, example, tabs):
        # TODO: support variables which are no reference
        var_type = type(example)
        key = 'example'
        recursive = False
        if var_type == str:
            if example[0] == '#':
                # if example is a #reference to another schema, create a reference
                self.check_if_schema_exists(example)  # check if schema exists
                var_type = dict  # set var_type to dict
                key = '$ref'  # change 'example' key to 'ref'
                example = "'#/components/schemas/{schema}'".format(schema=example[1:])  # refer to correct schema

                # For references in an array, the name will be #Reference, this has to be changed into Reference
                if name[0] == '#':
                    name = name[1:]
            else:
                # if no reference, regular string
                example = '\"{0}\"'.format(example)
        elif var_type in {dict, list}:
            # Schema contains recursive object or list, write it
            self.write_schema_values(name, example, tabs)
            return

        formatted_var_type = self.format_parameter_type(var_type)

        variable = inspect.cleandoc("""
                            {key}: {example}
                        """).format(name=name, type=formatted_var_type, example=example, key=key)

        variable = self.indent(variable, self.tab * tabs)
        self.file.write(variable)
        self.file.write("\n")

    def check_if_schema_exists(self, reference):
        schema_name = None
        if reference[0] == '#':
            schema_name = reference[1:]
        else:
            schema_name == reference

        schema = [x for x in self.schemas if list((x.keys()))[0] == schema_name]
        if schema is None:
            raise SwaggerGeneratorException(
                'Schema "{schema}" could not be found'.format(schema=schema_name)
            )
        else:
            return True
