import setuptools
from version import get_version

VERSION = get_version()

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name="flask-swagger-generator",
    version=VERSION,
    license="MIT",
    author="coding kitties",
    description="A library for generating swagger open api specifications for "
                "the Flask web framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/coding-kitties/flask-swagger-generator.git",
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    keywords=['Flask', 'swagger', 'swagger generator', 'OpenAPI'],
    classifiers=[
        "Intended Audience :: Developers",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        "Topic :: Software Development",
    ],
    install_requires=required,
    python_requires='>=3',
    include_package_data=True,
)
