from flask import Flask


def create_app():
    """
    Function to create a Flask app. The app will be based on the \
    given configuration from the client.
    """
    ref_app = Flask(__name__.split('.')[0])
    ref_app.url_map.strict_slashes = False
    return ref_app


app = create_app()
