import base64
from urllib.parse import quote
from .auth import BaseOAuthClient, Scope, TokenProviderInterface, SimpleTokenProvider, OAuthTokenProvider

BASE_URL = 'https://developer.api.autodesk.com/modelderivative/v2'
READ_SCOPES = [Scope.DataRead, Scope.ViewablesRead]
WRITE_SCOPES = [Scope.DataCreate, Scope.DataWrite, Scope.DataRead]

def urnify(text):
    """
    Convert input string into base64-encoded string (without padding '=' characters) that can be used
    as Model Derivative service URN.

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

    def __init__(self, token_provider: TokenProviderInterface(), base_url: str = BASE_URL):
        """
        Create new instance of the client.

        Args:
            token_provider (autodesk_forge_sdk.auth.TokenProviderInterface): Provider that will be used to generate access tokens for API calls.

                Use `autodesk_forge_sdk.auth.OAuthTokenProvider` if you have your app's client ID and client secret available,
                `autodesk_forge_sdk.auth.SimpleTokenProvider` if you would like to use an existing access token instead,
                or even your own implementation of the `autodesk_forge_sdk.auth.TokenProviderInterface` interface.
            base_url (str, optional): Base URL for API calls.

        Examples:
            ```
            FORGE_CLIENT_ID = os.environ["FORGE_CLIENT_ID"]
            FORGE_CLIENT_SECRET = os.environ["FORGE_CLIENT_SECRET"]
            client1 = ModelDerivativeClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))

            FORGE_ACCESS_TOKEN = os.environ["FORGE_ACCESS_TOKEN"]
            client2 = ModelDerivativeClient(SimpleTokenProvider(FORGE_ACCESS_TOKEN))

            class MyTokenProvider(autodesk_forge_sdk.auth.TokenProviderInterface):
                def get_token(self, scopes):
                    return "your own access token retrieved from wherever"
            client3 = ModelDerivativeClient(MyTokenProvider())
            ```
        """
        BaseOAuthClient.__init__(self, token_provider, base_url)

    def get_formats(self) -> dict:
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
            resp = client.get_formats()
            print(resp.formats)
            ```
        """
        return self._get('/designdata/formats', []).json()

    def submit_job(self, urn: str, output_formats: list[dict], output_region: str, root_filename: str=None, workflow_id: str=None, workflow_attr: str=None, force: bool = False) -> dict:
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
            URN = urnify("some-object-id")
            client = ModelDerivativeClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
            job = client.submit_job(URN, [{ "type": "svf", views: ["2d", "3d"] }], "US")
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

    def get_thumbnail(self, urn: str, width: int=None, height: int=None) -> bytes:
        """
        Download thumbnail for a source file.

        **Documentation**: https://forge.autodesk.com/en/docs/model-derivative/v2/reference/http/urn-thumbnail-GET

        Args:
            urn (str): Base64-encoded ID of the source file.
            width (int, optional): Width of thumbnail. Possible values: 100, 200, 400.

                If width is omitted, but height is specified, the implicit value for width will match height. If both
                width and height are omitted, the server will return a thumbnail closest to a width of 200, if available.
            height (int, optional): Height of thumbnail. Possible values: 100, 200, 400.

                If height is omitted, but width is specified, the implicit value for height will match width. If both
                width and height are omitted, the server will return a thumbnail closest to a width of 200, if available.

        Returns:
            bytes: buffer containing the thumbnail PNG image.

        Examples:
            ```
            FORGE_CLIENT_ID = os.environ["FORGE_CLIENT_ID"]
            FORGE_CLIENT_SECRET = os.environ["FORGE_CLIENT_SECRET"]
            URN = urnify("some-object-id")
            client = ModelDerivativeClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
            png = client.get_thumbnail(URN)
            with open("thumbnail.png", "wb") as output:
                output.write(png)
            ```
        """
        params = {}
        if width:
            params['width'] = width
        if height:
            params['height'] = height
        # TODO: what about the EMEA endpoint?
        resp = self._get('/designdata/{}/thumbnail'.format(urn), READ_SCOPES, params=params)
        return resp.content

    def get_manifest(self, urn: str) -> dict:
        """
        Retrieve the manifest for the source design specified by the urn URI parameter.
        The manifest is a list containing information about the derivatives generated while translating a source file.
        The manifest contains information such as the URNs of the derivatives, the translation status of each derivative,
        and much more.

        **Documentation**: https://forge.autodesk.com/en/docs/model-derivative/v2/reference/http/urn-manifest-GET

        Args:
            urn (str): Base64-encoded ID of the source file.

        Returns:
            dict: Parsed manifest JSON.

        Examples:
            ```
            FORGE_CLIENT_ID = os.environ["FORGE_CLIENT_ID"]
            FORGE_CLIENT_SECRET = os.environ["FORGE_CLIENT_SECRET"]
            URN = urnify("some-object-id")
            client = ModelDerivativeClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
            manifest = client.get_manifest(URN)
            print(manifest)
            ```
        """
        # TODO: what about the EMEA endpoint?
        return self._get('/designdata/{}/manifest'.format(urn), READ_SCOPES).json()

    def delete_manifest(self, urn: str):
        """
        Delete the manifest and all its translated output files (derivatives). However, it does not delete
        the design source file.

        **Documentation**: https://forge.autodesk.com/en/docs/model-derivative/v2/reference/http/urn-manifest-DELETE

        Args:
            urn (str): Base64-encoded ID of the source file.

        Examples:
            ```
            FORGE_CLIENT_ID = os.environ["FORGE_CLIENT_ID"]
            FORGE_CLIENT_SECRET = os.environ["FORGE_CLIENT_SECRET"]
            URN = urnify("some-object-id")
            client = ModelDerivativeClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
            client.delete_manifest(URN)
            ```
        """
        # TODO: what about the EMEA endpoint?
        self._delete('/designdata/{}/manifest'.format(urn), WRITE_SCOPES)

    def get_metadata(self, urn: str) -> dict:
        """
        Returns a list of model view (metadata) IDs for a design model. The metadata ID enables end users
        to select an object tree and properties for a specific model view.

        **Documentation**: https://forge.autodesk.com/en/docs/model-derivative/v2/reference/http/urn-metadata-GET

        Args:
            urn (str): Base64-encoded ID of the source file.

        Returns:
            dict: Parsed response JSON.

        Examples:
            ```
            FORGE_CLIENT_ID = os.environ["FORGE_CLIENT_ID"]
            FORGE_CLIENT_SECRET = os.environ["FORGE_CLIENT_SECRET"]
            URN = urnify("some-object-id")
            client = ModelDerivativeClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
            metadata = client.get_metadata(URN)
            print(metadata)
            ```
        """
        # TODO: what about the EMEA endpoint?
        return self._get('/designdata/{}/metadata'.format(urn), READ_SCOPES).json()

    def get_viewable_tree(self, urn: str, guid: str) -> dict:
        """
        Return an object tree, i.e., a hierarchical list of objects for a model view.

        **Documentation**: https://forge.autodesk.com/en/docs/model-derivative/v2/reference/http/urn-metadata-guid-GET

        Args:
            urn (str): Base64-encoded ID of the source file.
            guid (str): ID of one of the viewables extracted from the source file.

        Returns:
            dict: Parsed response JSON.

        Examples:
            ```
            FORGE_CLIENT_ID = os.environ["FORGE_CLIENT_ID"]
            FORGE_CLIENT_SECRET = os.environ["FORGE_CLIENT_SECRET"]
            URN = urnify("some-object-id")
            client = ModelDerivativeClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
            tree = client.get_viewable_tree(URN, "some-viewable-guid")
            print(tree)
            ```
        """
        # TODO: what about the EMEA endpoint?
        return self._get('/designdata/{}/metadata/{}'.format(urn, guid), READ_SCOPES).json()

    def get_viewable_properties(self, urn: str, guid: str) -> dict:
        """
        Return a list of properties for each object in an object tree. Properties are returned according to object ID
        and do not follow a hierarchical structure.

        **Documentation**: https://forge.autodesk.com/en/docs/model-derivative/v2/reference/http/urn-metadata-guid-properties-GET

        Args:
            urn (str): Base64-encoded ID of the source file.
            guid (str): ID of one of the viewables extracted from the source file.

        Returns:
            dict: Parsed response JSON.

        Examples:
            ```
            FORGE_CLIENT_ID = os.environ["FORGE_CLIENT_ID"]
            FORGE_CLIENT_SECRET = os.environ["FORGE_CLIENT_SECRET"]
            URN = urnify("some-object-id")
            client = ModelDerivativeClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
            props = client.get_viewable_properties(URN, "some-viewable-guid")
            print(props)
            ```
        """
        # TODO: what about the EMEA endpoint?
        return self._get('/designdata/{}/metadata/{}/properties'.format(urn, guid), READ_SCOPES).json()
