import setuptools
from flask_swagger_generator import get_version

VERSION = get_version()

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name="flask-swagger-generator",
    version=VERSION,
    license="BSL-1.1",
    author="coding kitties",
    description="A library for generating swagger specifications for "
                "the Flask web framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/coding-kitties/flask-swagger-generator.git",
    download_url='https://github.com/coding-kitties/investing-algorithm-framework/archive/{}.tar.gz'.format(VERSION),
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    keywords=['Flask', 'swagger', 'swagger generator', 'OpenAPI'],
    classifiers=[
        "Intended Audience :: Developers",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        "Topic :: Software Development",
        "License :: MIT",
    ],
    install_requires=required,
    python_requires='>=3.6',
    include_package_data=True,
)