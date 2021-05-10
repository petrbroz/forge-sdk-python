Sample Django application using the [autodesk-forge-sdk](https://pypi.org/project/autodesk-forge-sdk) Python package.

## Usage

- install dependencies: `make init`
- set the following environment variables:
    - `FORGE_CLIENT_ID` - your Forge app's client ID
    - `FORGE_CLIENT_SECRET` - your Forge app's client secret
    - `FORGE_BUCKET` - name of an existing bucket in Forge Data Management service
- run the Django app: `make run`
- go to http://localhost:8000
