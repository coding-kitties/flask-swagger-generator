import inspect
from logging import getLogger

from marshmallow import fields

from flask_swagger_generator.components.swagger_models import SwaggerModel
from flask_swagger_generator.components.version_three.schema_attribute import \
    SwaggerSchemaAttribute
from flask_swagger_generator.exceptions import SwaggerGeneratorException
from flask_swagger_generator.utils import PropertyType

logger = getLogger(__name__)


class SwaggerSchema(SwaggerModel):

    def __init__(self, schema=None, reference_name=None, name=None):
        super(SwaggerSchema, self).__init__()
        self.reference_name = reference_name
        self.name = self.reference_name

        if name is not None:
            self.name = name

        if schema is not None:
            nested_schemas = []

            for attribute in schema:

                if isinstance(schema[attribute], dict):
                    reference_name = \
                        f'"#/components/schemas/{attribute}' \
                        f'_{self.reference_name}"'
                    self.add_swagger_model(
                        SwaggerSchemaAttribute(
                            name=attribute,
                            reference=reference_name,
                        )
                    )
                    nested_schemas.append(
                        SwaggerSchema(
                            schema=schema[attribute],
                            reference_name=f"{attribute}_{self.reference_name}",
                            name=attribute
                        )
                    )

                else:
                    self.add_swagger_model(
                        SwaggerSchemaAttribute(
                            name=attribute, value=schema[attribute]
                        )
                    )

            self.swagger_models += nested_schemas

    def perform_write(self, file):

        if len(self.swagger_models) == 0:
            schema_entry = inspect.cleandoc(
                """
                    {name}:
                      type: object
                """.format(name=self.reference_name)
            )
            schema_entry = self.indent(schema_entry, 2 * self.TAB)
            file.write(schema_entry)
            file.write('\n')
        else:
            schema_entry = inspect.cleandoc(
                """
                    {name}:
                      type: object
                      properties:
                """.format(name=self.reference_name)
            )
            schema_entry = self.indent(schema_entry, 2 * self.TAB)
            file.write(schema_entry)
            file.write('\n')


class SwaggerMashmallowSchema(SwaggerSchema):

    def __init__(self, schema=None, reference_name=None, name=None):
        super(SwaggerMashmallowSchema, self)\
            .__init__(reference_name=reference_name, name=name)

        nested_schemas = []

        for field in schema.fields:

            if isinstance(schema.fields[field], fields.Nested):
                name = f'{field}_{self.reference_name}'
                full_reference = f'"#/components/schemas/' \
                                 f'{field}_{self.reference_name}"'
                nested_schemas.append(
                    SwaggerMashmallowSchema(
                        schema=schema.fields[field].nested,
                        reference_name=name
                    )
                )
                self.swagger_models.append(
                    SwaggerSchemaAttribute(
                        name=field,
                        reference=full_reference
                    )
                )
            else:
                try:
                    self.swagger_models.append(
                        SwaggerSchemaAttribute(
                            name=field,
                            type=self.get_marshmallow_type(schema.fields[field])
                        )
                    )
                except SwaggerGeneratorException as e:
                    logger.error(e)

        self.swagger_models += nested_schemas


    @staticmethod
    def get_marshmallow_type(value):

        if isinstance(value, fields.Integer):
            return PropertyType.INTEGER
        elif isinstance(value, fields.String):
            return PropertyType.STRING
        elif isinstance(value, fields.Float):
            return PropertyType.NUMBER
        elif isinstance(value, fields.List):
            return PropertyType.ARRAY
        elif isinstance(value, fields.Email):
            return PropertyType.STRING
        elif isinstance(value, fields.Boolean):
            return PropertyType.BOOLEAN
        elif isinstance(value, fields.DateTime):
            return PropertyType.DATE_TIME
        elif isinstance(value, fields.URL):
            return PropertyType.STRING
        else:
            raise SwaggerGeneratorException(
                "Type {} is not supported".format(type(value))
            )
