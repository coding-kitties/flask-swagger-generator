# Flask Swagger Generator
Flask swagger generator is a library to create Swagger Open API definitions 
for Flask based applications. Swagger is an Interface Description Language for describing REST 
APIs expressed using JSON and YAML. 

## Installing 
Install and update using pip:

```
pip install flask-swagger-generator
```

## A Simple Example

```python
from flask import Blueprint, jsonify
from flask import Flask

from flask_swagger_generator.generators import Generator
from flask_swagger_generator.specifiers import SwaggerVersion
from flask_swagger_generator.utils import SecurityType

# Create the bluepints
blueprint = Blueprint('objects', __name__)

# Create the flask app
app = Flask(__name__)

# Create swagger version 3.0 generator
generator = Generator.of(SwaggerVersion.VERSION_THREE)

# Add security, response and request body definitions
@generator.security(SecurityType.BEARER_AUTH)
@generator.response(status_code=200, schema={'id': 10, 'name': 'test_object'})
@generator.request_body({'id': 10, 'name': 'test_object'})
@blueprint.route('/objects/<int:object_id>', methods=['PUT'])
def update_object(object_id):
    return jsonify({'id': 1, 'name': 'test_object_name'}), 201

app.register_blueprint(blueprint)
```