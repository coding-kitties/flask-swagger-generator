from tests.resources.test_app import create_app
from flask import Blueprint, jsonify
from flask_swagger_generator.generators import Generator
from flask_swagger_generator.specifiers import SwaggerVersion
from flask_swagger_generator.utils import SecurityType

from marshmallow import Schema, fields

class ObjectSerializer(Schema):
    id = fields.Integer()
    name = fields.String()


class ObjectChildDeserializer(Schema):
    id = fields.Integer()
    name = fields.String()


class ObjectDeserializer(Schema):
    attribute_one = fields.Int()
    attribute_two = fields.Str()
    attribute_three = fields.Email()
    attribute_four = fields.Boolean()
    attribute_five = fields.URL()
    attribute_six = fields.Nested(ObjectChildDeserializer(many=False))


class TestVersionThreeAPI():
    
    def __init__(self):
        self.app = create_app()
        self.generator = Generator.of(SwaggerVersion.VERSION_THREE)
        self.blueprint = Blueprint('objects', __name__)
        self.create_test_api()
        self.app.register_blueprint(self.blueprint)

    def create_test_api(self):

        generator = self.generator
        blueprint = self.blueprint

        schema_two = generator.create_schema(
        'schema_two', {'id': 10, 'name': 'test_object'}
        )
        schema_three = generator.create_schema('schema_three', ObjectDeserializer())


        @generator.response(200, schema_two)
        @blueprint.route('/objects/<int:object_id>', methods=['GET'])
        def retrieve_object(object_id, child_id):
            return jsonify({'objects': []}), 200


        @generator.response(204, schema_two)
        @generator.security(SecurityType.BEARER_AUTH)
        @blueprint.route('/objects/<int:object_id>', methods=['DELETE'])
        def delete_object(object_id):
            return jsonify({'objects': []}), 200


        @generator.response(200, schema_two)
        @generator.security(SecurityType.BEARER_AUTH)
        @generator.request_body(schema_three)
        @blueprint.route('/objects/<int:object_id>', methods=['PUT'])
        def update_object(object_id):
            pass


        @generator.response(status_code=201, schema={'id': 10, 'name': 'test_object'})
        @generator.request_body({'id': 10, 'name': 'test_object'})
        @blueprint.route('/objects/<int:object_id>', methods=['POST'])
        def create_object(object_id):
            return jsonify({'objects': []}), 200