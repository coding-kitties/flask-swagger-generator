import os
import pathlib

from deepdiff import DeepDiff
from flask import Blueprint, jsonify
from flask_testing import TestCase
from marshmallow import Schema, fields

from flask_swagger_generator.generators import Generator
from flask_swagger_generator.components import SwaggerVersion
from flask_swagger_generator.utils import SecurityType
from tests.resources.app_base import create_app
from tests.resources.utils import yaml_as_dict

app = create_app()
generator = Generator.of(SwaggerVersion.VERSION_THREE)
blueprint = Blueprint('objects', __name__)


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


query_params = [
    {
        "name": "param1",
        "type": "string",
    },
    {
        "name": "param2",
        "type": "int",
    }
]


@generator.response(200, ObjectSerializer())
@generator.query_parameters(query_params)
@blueprint.route('/objects', methods=['GET'])
def list_objects():
    return jsonify({'objects': []}), 200


@generator.response(200, ObjectSerializer())
@blueprint.route('/objects/<int:object_id>', methods=['GET'])
def retrieve_object(object_id, child_id):
    return jsonify({'objects': []}), 200


@generator.response(204, ObjectSerializer())
@generator.security(SecurityType.BEARER_AUTH)
@blueprint.route('/objects/<int:object_id>', methods=['DELETE'])
def delete_object(object_id):
    return jsonify({'objects': []}), 200


@generator.response(200, ObjectSerializer())
@generator.security(SecurityType.BEARER_AUTH)
@generator.request_body(ObjectDeserializer())
@blueprint.route('/objects/<int:object_id>', methods=['PUT'])
def update_object(object_id):
    return jsonify({'objects': []}), 200


@generator.response(status_code=201, schema={'id': 10, 'name': 'test_object'})
@generator.request_body({'id': 10, 'name': 'test_object'})
@blueprint.route('/objects/<int:object_id>', methods=['POST'])
def create_object(object_id):
    return jsonify({'objects': []}), 200


app.register_blueprint(blueprint)


class AppTestBase(TestCase):

    def setUp(self) -> None:
        super(AppTestBase, self).setUp()

    def create_app(self):
        return app

    def tearDown(self):
        super(AppTestBase, self).tearDown()

    def test(self):
        generated_swagger_path = os.path.join(
            pathlib.Path(__file__).parent.parent.absolute()
        ) + '/resources/generated.yaml'
        correct_swagger_path = os.path.join(
            pathlib.Path(__file__).parent.parent.absolute()
        ) + '/resources/swagger_version_three/marshmallow_swagger.yaml'
        generator.generate_swagger(self.app, generated_swagger_path)
        generated_yaml = yaml_as_dict(generated_swagger_path)
        reference_yaml = yaml_as_dict(correct_swagger_path)
        reference_yaml['info'].pop('description')
        generated_yaml['info'].pop('description')
        difference = DeepDiff(generated_yaml, reference_yaml, ignore_order=True)
        self.assertEqual({}, difference)
