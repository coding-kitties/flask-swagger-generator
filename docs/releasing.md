# Releasing a new version of the library

This document describes the process of releasing a new version of the library.

## Prerequisites
- You are a maintainer of the repository
- You are allowed to push to master

## Steps
1. Checkout develop
2. Update the version in `version.py` 
   > Note: The version should follow [semantic versioning](https://semver.org/)
3. Make a pull request to master from the develop branch.
4. Once the pull request is merged, create a tag with the version number your local main branch.
5. Push the tag to the remote repository on the main branch.
6. A new version of the library will be released automatically once the checks have passed.

## Troubleshooting
For any questions or discussions, please start a conversation \
in the [discussions tab](https://github.com/coding-kitties/flask-swagger-generator/discussions/35).
