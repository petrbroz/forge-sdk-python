import base64
from urllib.parse import quote
from .auth import BaseOAuthClient, Scope, TokenProviderInterface

BASE_URL = 'https://developer.api.autodesk.com/modelderivative/v2'
WRITE_SCOPES = [Scope.DataCreate, Scope.DataWrite, Scope.DataRead]

def urnify(text):
    """
    Convert input string into base64-encoded string (without padding '=' characters) that can be used as Model Derivative service URN.

    Args:
        text (str): Input text.

    Returns:
        str: Base64-encoded string.

    Examples:
        ```
        text = "Hello World"
        encoded = urnify(text)
        print(encoded)
        ```
    """
    base64_bytes = base64.b64encode(text.encode('ascii'))
    ascii_output = base64_bytes.decode('ascii')
    return ascii_output.rstrip('=')

class ModelDerivativeClient(BaseOAuthClient):
    """
    Forge Model Derivative service client.

    **Documentation**: https://forge.autodesk.com/en/docs/model-derivative/v2/reference/http
    """

    def __init__(self, token_provider, base_url=BASE_URL):
        """
        Create new instance of the client.

        Args:
            token_provider (TokenProviderInterface): Provider that will be used to generate access tokens for API calls.
            base_url (str, optional): Base URL for API calls.
        """
        BaseOAuthClient.__init__(self, token_provider, base_url)

    def get_formats(self):
        """
        Return an up-to-date list of Forge-supported translations, that you can use to identify
        which types of derivatives are supported for each source file type.

        **Documentation**: https://forge.autodesk.com/en/docs/model-derivative/v2/reference/http

        Returns:
            dict: Parsed response JSON.

        Examples:
            ```
            FORGE_CLIENT_ID = os.environ["FORGE_CLIENT_ID"]
            FORGE_CLIENT_SECRET = os.environ["FORGE_CLIENT_SECRET"]
            client = ModelDerivativeClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
            formats = client.get_formats()
            print(formats)
            ```
        """
        return self._get('/designdata/formats', []).json()

    def submit_job(self, urn, output_formats, output_region, root_filename=None, workflow_id=None, workflow_attr=None, force=False):
        """
        Translate a design from one format to another format.

        **Documentation**: https://forge.autodesk.com/en/docs/model-derivative/v2/reference/http/job-POST

        Args:
            urn (str): Base64-encoded ID of the object to translate.
            output_formats (list[dict]): List of objects representing all the requested outputs. Each object should have at least `type` property set to 'svf', 'svf2', etc.
            output_region (str): Output region. Allowed values: 'US', 'EMEA'.
            root_filename (str, optional): Starting filename if the converted file is a ZIP archive.
            workflow_id (str, optional): Workflow ID.
            workflow_attr (str, optional): Workflow payload.

        Returns:
            dict: Parsed response JSON.

        Examples:
            ```
            FORGE_CLIENT_ID = os.environ["FORGE_CLIENT_ID"]
            FORGE_CLIENT_SECRET = os.environ["FORGE_CLIENT_SECRET"]
            client = ModelDerivativeClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
            job = client.submit_job(urn, [{ "type": "svf", views: ["2d", "3d"] }], "US")
            print(job)
            ```
        """
        json = {
            'input': {
                'urn': urn
            },
            'output': {
                'formats': output_formats,
                'destination': {
                    'region': output_region
                }
            }
        }
        if root_filename:
            json['input']['compressedUrn'] = True
            json['input']['rootFilename'] = root_filename
        if workflow_id:
            json['misc'] = { 'workflowId': workflow_id }
            if workflow_attr:
                json['misc']['workflowAttribute'] = workflow_attr
        headers = {}
        if force:
            headers['x-ads-force'] = 'true'
        # TODO: what about the EMEA endpoint?
        return self._post('/designdata/job', WRITE_SCOPES, json=json, headers=headers).json()