import os
from deepdiff import DeepDiff
import pathlib

from flask_testing import TestCase

from tests.resources.utils import yaml_as_dict
from tests.resources.test_apis import TestVersionThreeAPI



class AppTestBase(TestCase):

    def setUp(self) -> None:
        super(AppTestBase, self).setUp()

    def create_app(self):
        self.api = TestVersionThreeAPI()
        self.generator = self.api.generator
        return self.api.app  

    def tearDown(self):
        super(AppTestBase, self).tearDown()


class TestGenerateSwaggerV3(AppTestBase):

    def setUp(self) -> None:
        self.generated_path = os.path.join(
            pathlib.Path(__file__).parent.absolute()
        ) + '/resources/generated.yaml'
        
        self.reference_path = os.path.join(
                pathlib.Path(__file__).parent.absolute()
            ) + '/resources/reference_version_three.yaml'

    def tearDown(self):
        os.remove(self.generated_path)
    
    def test_with_dest_path(self):

        self.generator.generate_swagger(
            self.app, self.generated_path
        )

        self.verify_output(self.generated_path, self.reference_path)

    def test_without_dest_path(self):

        self.generated_path = os.path.join(
            pathlib.Path(__file__).parent.parent.absolute()
        ) + '/swagger.yaml'

        self.generator.generate_swagger(self.app)

        self.verify_output(self.generated_path, self.reference_path)

    def test_server_url(self):
        server_url = "http://localhost:8000"

        self.generator.generate_swagger(
            self.app, self.generated_path, server_url=server_url
        )

        generated_yaml, reference_yaml = \
            self.yaml_as_dict(self.generated_path, self.reference_path)

        reference_yaml['servers'][0]['url'] = server_url

        difference = DeepDiff(generated_yaml, reference_yaml, ignore_order=True)
        self.assertEqual({}, difference)
        

    def yaml_as_dict(self, generated_path, reference_path):
        generated_yaml = yaml_as_dict(generated_path)
        reference_yaml = yaml_as_dict(reference_path)

        reference_yaml['info'].pop('description')
        generated_yaml['info'].pop('description')

        return generated_yaml, reference_yaml

    def verify_output(self, generated_path, reference_path):
        generated_yaml, reference_yaml = \
             self.yaml_as_dict(generated_path, reference_path)
        difference = DeepDiff(generated_yaml, reference_yaml, ignore_order=True)
        self.assertEqual({}, difference)
