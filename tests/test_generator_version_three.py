from flask_testing import TestCase
from tests.resources.test_app import create_app
from flask import Blueprint, jsonify
from flask_swagger_generator.generators import Generator
from flask_swagger_generator.specifiers import SwaggerVersion


app = create_app()

generator = Generator.of(SwaggerVersion.VERSION_THREE)
blueprint = Blueprint('objects', __name__)


@generator.response(
    status_code=200, schema={'response': []}
)
@blueprint.route('/objects', methods=['GET'])
def list_objects():
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
        generator.generate_swagger(self.app)


