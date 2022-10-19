import os
from deepdiff import DeepDiff
import pathlib

from flask_testing import TestCase

from tests.resources.utils import yaml_as_dict
from tests.resources.test_apis import TestAPI



class AppTestBase(TestCase):

    def setUp(self) -> None:
        super(AppTestBase, self).setUp()

    def create_app(self):
        self.api = TestAPI()
        return self.api.app

    def tearDown(self):
        super(AppTestBase, self).tearDown()


class TestGenerateSwagger(AppTestBase):
    
    def test_with_dest_path(self):

        generated_path = os.path.join(
            pathlib.Path(__file__).parent.absolute()
        ) + '/resources/generated.yaml'

        reference_path = os.path.join(
            pathlib.Path(__file__).parent.absolute()
        ) + '/resources/reference_version_three.yaml'

        generator = self.api.generator

        generator.generate_swagger(
            self.app, generated_path
        )

        self.verify_output(generated_path, reference_path)


    def test_without_dest_path(self):

        generated_path = os.path.join(
            pathlib.Path(__file__).parent.parent.absolute()
        ) + '/swagger.yaml'

        reference_path = os.path.join(
            pathlib.Path(__file__).parent.absolute()
        ) + '/resources/reference_version_three.yaml'

        generator = self.api.generator

        generator.generate_swagger(
            self.app, generated_path
        )

        self.verify_output(generated_path, reference_path)

    def verify_output(self, generated_path, reference_path):
        generated_yaml = yaml_as_dict(generated_path)
        reference_yaml = yaml_as_dict(reference_path)

        reference_yaml['info'].pop('description')
        generated_yaml['info'].pop('description')

        difference = DeepDiff(generated_yaml, reference_yaml, ignore_order=True)
        self.assertEqual({}, difference)
        os.remove(generated_path)
