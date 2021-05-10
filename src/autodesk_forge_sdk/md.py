"""
Clients for working with the Forge Model Derivative service.
"""

import base64
from .auth import BaseOAuthClient, Scope, TokenProviderInterface

BASE_URL = "https://developer.api.autodesk.com/modelderivative/v2"
READ_SCOPES = [Scope.DATA_READ, Scope.VIEWABLES_READ]
WRITE_SCOPES = [Scope.DATA_CREATE, Scope.DATA_WRITE, Scope.DATA_READ]


def urnify(text):
    """
    Convert input string into base64-encoded string (without padding "=" characters)
    that can be used as Model Derivative service URN.

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
    base64_bytes = base64.b64encode(text.encode("ascii"))
    ascii_output = base64_bytes.decode("ascii")
    return ascii_output.rstrip("=")


class ModelDerivativeClient(BaseOAuthClient):
    """
    Forge Model Derivative service client.

    **Documentation**: https://forge.autodesk.com/en/docs/model-derivative/v2/reference/http
    """

    def __init__(self, token_provider: TokenProviderInterface(), base_url: str = BASE_URL):
        """
        Create new instance of the client.

        Args:
            token_provider (autodesk_forge_sdk.auth.TokenProviderInterface):
                Provider that will be used to generate access tokens for API calls.

                Use `autodesk_forge_sdk.auth.OAuthTokenProvider` if you have your app's client ID
                and client secret available, `autodesk_forge_sdk.auth.SimpleTokenProvider`
                if you would like to use an existing access token instead, or even your own
                implementation of the `autodesk_forge_sdk.auth.TokenProviderInterface` interface.
            base_url (str, optional): Base URL for API calls.

        Examples:
            ```
            FORGE_CLIENT_ID = os.environ["FORGE_CLIENT_ID"]
            FORGE_CLIENT_SECRET = os.environ["FORGE_CLIENT_SECRET"]
            client1 = ModelDerivativeClient(
                OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))

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
        return self._get("/designdata/formats", scopes=[]).json()

    def submit_job(self, urn: str, output_formats: list[dict], **kwargs) -> dict:
        """
        Translate a design from one format to another format.

        **Documentation**:
            https://forge.autodesk.com/en/docs/model-derivative/v2/reference/http/job-POST

        Args:
            urn (str): Base64-encoded ID of the object to translate.
            output_formats (list[dict]): List of objects representing all the requested outputs.
                Each object should have at least `type` property set to "svf", "svf2", etc.
            output_region (str): Output region. Allowed values: "US", "EMEA".
            root_filename (str, optional): Starting filename if the converted file is a ZIP archive.
            workflow_id (str, optional): Workflow ID.
            workflow_attr (str, optional): Workflow payload.
            force (bool, optional): Force the processing of a model
                that has already been translated before.

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
            "input": {
                "urn": urn
            },
            "output": {
                "formats": output_formats,
                "destination": {
                    "region": kwargs["output_region"] if "output_region" in kwargs else "US"
                }
            }
        }
        if "root_filename" in kwargs:
            json["input"]["compressedUrn"] = True
            json["input"]["rootFilename"] = kwargs["root_filename"]
        if "workflow_id" in kwargs:
            json["misc"] = { "workflowId": kwargs["workflow_id"] }
            if "workflow_attr" in kwargs:
                json["misc"]["workflowAttribute"] = kwargs["workflow_attr"]
        headers = {}
        if "force" in kwargs:
            headers["x-ads-force"] = "true"
        # TODO: what about the EMEA endpoint?
        return self._post("/designdata/job", WRITE_SCOPES, json=json, headers=headers).json()

    def get_thumbnail(self, urn: str, width: int = None, height: int = None) -> bytes:
        """
        Download thumbnail for a source file.

        **Documentation**:
            https://forge.autodesk.com/en/docs/model-derivative/v2/reference/http/urn-thumbnail-GET

        Args:
            urn (str): Base64-encoded ID of the source file.
            width (int, optional): Width of thumbnail. Possible values: 100, 200, 400.

                If width is omitted, but height is specified, the implicit value for width
                will match height. If both width and height are omitted, the server
                will return a thumbnail closest to a width of 200, if available.
            height (int, optional): Height of thumbnail. Possible values: 100, 200, 400.

                If height is omitted, but width is specified, the implicit value for height
                will match width. If both width and height are omitted, the server
                will return a thumbnail closest to a width of 200, if available.

        Returns:
            bytes: buffer containing the thumbnail PNG image.

        Examples:
            ```
            FORGE_CLIENT_ID = os.environ["FORGE_CLIENT_ID"]
            FORGE_CLIENT_SECRET = os.environ["FORGE_CLIENT_SECRET"]
            URN = urnify("some-object-id")
            client = ModelDerivativeClient(
                OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
            png = client.get_thumbnail(URN)
            with open("thumbnail.png", "wb") as output:
                output.write(png)
            ```
        """
        params = {}
        if width:
            params["width"] = width
        if height:
            params["height"] = height
        # TODO: what about the EMEA endpoint?
        endpoint = "/designdata/{}/thumbnail".format(urn)
        return self._get(endpoint, scopes=READ_SCOPES, params=params).content

    def get_manifest(self, urn: str) -> dict:
        """
        Retrieve the manifest for the source design specified by the urn URI parameter.
        The manifest is a list containing information about the derivatives generated
        while translating a source file. The manifest contains information such as the URNs
        of the derivatives, the translation status of each derivative, and much more.

        **Documentation**:
            https://forge.autodesk.com/en/docs/model-derivative/v2/reference/http/urn-manifest-GET

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
        endpoint = "/designdata/{}/manifest".format(urn)
        return self._get(endpoint, scopes=READ_SCOPES).json()

    def delete_manifest(self, urn: str):
        """
        Delete the manifest and all its translated output files (derivatives).
        However, it does not delete the design source file.

        **Documentation**:
            https://forge.autodesk.com/en/docs/model-derivative/v2/reference/http/urn-manifest-DELETE

        Args:
            urn (str): Base64-encoded ID of the source file.

        Examples:
            ```
            FORGE_CLIENT_ID = os.environ["FORGE_CLIENT_ID"]
            FORGE_CLIENT_SECRET = os.environ["FORGE_CLIENT_SECRET"]
            URN = urnify("some-object-id")
            client = ModelDerivativeClient(
                OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
            client.delete_manifest(URN)
            ```
        """
        # TODO: what about the EMEA endpoint?
        endpoint = "/designdata/{}/manifest".format(urn)
        self._delete(endpoint, scopes=WRITE_SCOPES)

    def get_metadata(self, urn: str) -> dict:
        """
        Returns a list of model view (metadata) IDs for a design model. The metadata ID enables
        end users to select an object tree and properties for a specific model view.

        **Documentation**:
            https://forge.autodesk.com/en/docs/model-derivative/v2/reference/http/urn-metadata-GET

        Args:
            urn (str): Base64-encoded ID of the source file.

        Returns:
            dict: Parsed response JSON.

        Examples:
            ```
            FORGE_CLIENT_ID = os.environ["FORGE_CLIENT_ID"]
            FORGE_CLIENT_SECRET = os.environ["FORGE_CLIENT_SECRET"]
            URN = urnify("some-object-id")
            client = ModelDerivativeClient(
                OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
            metadata = client.get_metadata(URN)
            print(metadata)
            ```
        """
        # TODO: what about the EMEA endpoint?
        endpoint = "/designdata/{}/metadata".format(urn)
        return self._get(endpoint, scopes=READ_SCOPES).json()

    def get_viewable_tree(self, urn: str, guid: str) -> dict:
        """
        Return an object tree, i.e., a hierarchical list of objects for a model view.

        **Documentation**:
            https://forge.autodesk.com/en/docs/model-derivative/v2/reference/http/urn-metadata-guid-GET

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
            client = ModelDerivativeClient(
                OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
            tree = client.get_viewable_tree(URN, "some-viewable-guid")
            print(tree)
            ```
        """
        # TODO: what about the EMEA endpoint?
        endpoint = "/designdata/{}/metadata/{}".format(urn, guid)
        return self._get(endpoint, scopes=READ_SCOPES).json()

    def get_viewable_properties(self, urn: str, guid: str) -> dict:
        """
        Return a list of properties for each object in an object tree. Properties are returned
        according to object ID and do not follow a hierarchical structure.

        **Documentation**:
            https://forge.autodesk.com/en/docs/model-derivative/v2/reference/http/urn-metadata-guid-properties-GET

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
        endpoint = "/designdata/{}/metadata/{}/properties".format(urn, guid)
        return self._get(endpoint, scopes=READ_SCOPES).json()

    def get_derivative_info(self, urn: str, deriv_urn: str) -> dict:
        """
        Return information about the specified derivative.

        **Documentation**:
            https://forge.autodesk.com/en/docs/model-derivative/v2/reference/http/urn-manifest-derivativeurn-HEAD

        Args:
            urn (str): Base64-encoded ID of the source file.
            deriv_urn (str): ID of one of the derivatives generated from the source file.

        Returns:
            dict: Derivative information, currently with just a single property, "size",
            indicating the size of the derivative in bytes.
        """
        # TODO: what about the EMEA endpoint?
        endpoint = "/designdata/{}/manifest/{}".format(urn, deriv_urn)
        resp = self._head(endpoint, scopes=READ_SCOPES)
        return { "size": int(resp.headers["Content-Length"]) }

    def get_derivative(self, urn: str, deriv_urn: str, byte_range: tuple=None) -> bytes:
        """
        Download a derivative generated from a specific source model. To download the derivative,
        you need to specify its URN which can be retrieved from the Model Derivative manifest.

        **Documentation**:
            https://forge.autodesk.com/en/docs/model-derivative/v2/reference/http/urn-manifest-derivativeurn-GET

        Args:
            urn (str): Base64-encoded ID of the source file.
            deriv_urn (str): ID of one of the derivatives generated from the source file.
            byte_range ((int,int), optional): Optional tuple with first and last byte
                of a range to download.

        Returns:
            bytes: Derivative content.
        """
        # TODO: what about the EMEA endpoint?
        endpoint = "/designdata/{}/manifest/{}".format(urn, deriv_urn)
        headers = {}
        if byte_range:
            headers["Range"] = "bytes={}-{}".format(byte_range[0], byte_range[1])
        return self._get(endpoint, scopes=READ_SCOPES, headers=headers).content

    def get_derivative_chunked(self, urn: str, deriv_urn: str, chunk_size: int=1024*1024) -> bytes:
        """
        Download complete derivative in chunks of specific size.

        **Documentation**:
            https://forge.autodesk.com/en/docs/model-derivative/v2/reference/http/urn-manifest-derivativeurn-GET

        Args:
            urn (str): Base64-encoded ID of the source file.
            deriv_urn (str): ID of one of the derivatives generated from the source file.
            chunk_size (int, optional): Size of individual chunks (in bytes).

        Returns:
            bytes: Derivative content.
        """
        deriv_info = self.get_derivative_info(urn, deriv_urn)
        buff = bytes()
        # TODO: what about the EMEA endpoint?
        downloaded_bytes = 0
        while downloaded_bytes < deriv_info["size"]:
            byte_range = (
                downloaded_bytes,
                min(downloaded_bytes + chunk_size - 1, deriv_info["size"] - 1)
            )
            # TODO: better way to concat buffers in memory?
            buff = buff + self.get_derivative(urn, deriv_urn, byte_range)
            downloaded_bytes += byte_range[1] - byte_range[0] + 1
        return buff
