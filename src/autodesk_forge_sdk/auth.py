import requests
from enum import Enum
from datetime import datetime, timedelta
from urllib.parse import quote
from .base import BaseClient

BASE_URL = 'https://developer.api.autodesk.com/authentication/v1'

class Scope(Enum):
    """
    Authentication scopes.
    """
    UserProfileRead = 'user-profile:read'
    """The application will be able to read the end user’s profile data (not including associated products and services)."""
    UserRead = 'user:read'
    """The application will be able to read the end user’s profile data, including associated products and services."""
    UserWrite = 'user:write'
    """The application will be able to create, update, and delete the end user’s profile data, including associated products and services."""
    ViewablesRead = 'viewables:read'
    """The application will only be able to read the end user’s viewable data (e.g., PNG and SVF files) within the Autodesk ecosystem."""
    DataRead = 'data:read'
    """The application will be able to read all the end user’s data (viewable and non-viewable) within the Autodesk ecosystem."""
    DataWrite = 'data:write'
    """The application will be able to create, update, and delete data on behalf of the end user within the Autodesk ecosystem."""
    DataCreate = 'data:create'
    """The application will be able to create data on behalf of the end user within the Autodesk ecosystem."""
    DataSearch = 'data:search'
    """The application will be able to search the end user’s data within the Autodesk ecosystem."""
    BucketCreate = 'bucket:create'
    """The application will be able to create an OSS bucket it will own."""
    BucketRead = 'bucket:read'
    """The application will be able to read the metadata and list contents for OSS buckets that it has access to."""
    BucketUpdate = 'bucket:update'
    """The application will be able to set permissions and entitlements for OSS buckets that it has permission to modify."""
    BucketDelete = 'bucket:delete'
    """The application will be able to delete a bucket that it has permission to delete."""
    CodeAll = 'code:all'
    """The application will be able to author and execute code on behalf of the end user (e.g., scripts processed by the Design Automation API)."""
    AccountRead = 'account:read'
    """For Product APIs, the application will be able to read the account data the end user has entitlements to."""
    AccountWrite = 'account:wriet'
    """For Product APIs, the application will be able to update the account data the end user has entitlements to."""

class AuthenticationClient(BaseClient):
    """
    Forge Authentication service client.

    **Documentation**: https://forge.autodesk.com/en/docs/oauth/v2/reference/http
    """

    def __init__(self, base_url: str=BASE_URL):
        """
        Create new instance of the client.

        Args:
            base_url (str, optional): Base URL for API calls.
        """
        BaseClient.__init__(self, base_url)

    def authenticate(self, client_id: str, client_secret: str, scopes: list[Scope]) -> dict:
        """
        Generate a two-legged access token for specific set of scopes.

        **Documentation**: https://forge.autodesk.com/en/docs/oauth/v2/reference/http/authenticate-POST

        Args:
            client_id (str): Client ID of the app.
            client_secret (str): Client secret of the app.
            scopes (list[Scope]): List of required scopes.

        Returns:
            dict: Parsed response object with properties `access_token`, `token_type`, and `expires_in`.

        Examples:
            ```
            FORGE_CLIENT_ID = os.environ["FORGE_CLIENT_ID"]
            FORGE_CLIENT_SECRET = os.environ["FORGE_CLIENT_SECRET"]
            client = AuthenticationClient()
            auth = client.authenticate(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET, [Scope.ViewablesRead])
            print(auth["access_token"])
            ```
        """
        form = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials',
            'scope': ' '.join(map(lambda s: s.value, scopes))
        }
        return self._post('/authenticate', form=form).json()

    def get_authorization_url(self, client_id: str, response_type: str, redirect_uri: str, scopes: list[Scope], state: str=None) -> str:
        """
        Generate a URL to redirect an end user to in order to acquire the user’s consent
        for your app to access the specified resources.

        **Documentation**: https://forge.autodesk.com/en/docs/oauth/v2/reference/http/authorize-GET

        Args:
            client_id (str): Client ID of the app.
            response_type (str): Must be either 'code' for authorization code grant flow or 'token' for implicit grant flow.
            redirect_uri (str): URL-encoded callback URL that the end user will be redirected to after completing the authorization flow.
            scopes (list[Scope]): List of required scopes.
            state (str, optional): Payload containing arbitrary data that the authentication flow will pass back verbatim in a state query parameter to the callback URL.

        Returns:
            str: Complete authorization URL.

        Examples:
            ```
            FORGE_CLIENT_ID = os.environ["FORGE_CLIENT_ID"]
            client = AuthenticationClient()
            url = client.get_authorization_url(FORGE_CLIENT_ID, "code", "http://localhost:3000/callback", [Scope.ViewablesRead])
            print(url)
            ```
        """
        url = 'https://developer.api.autodesk.com/authentication/v1/authorize'
        url = url + '?client_id={}'.format(quote(client_id))
        url = url + '&response_type={}'.format(response_type)
        url = url + '&redirect_uri={}'.format(quote(redirect_uri))
        url = url + '&scope={}'.format(quote(' '.join(map(lambda s: s.value, scopes))))
        if state:
            url += '&state={}'.format(quote(state))
        return url

    def get_token(self, client_id: str, client_secret: str, code: str, redirect_uri: str) -> dict:
        """
        Exchange an authorization code extracted from `get_authorization_url` callback for a three-legged access token.
        This API will only be used when the 'Authorization Code' grant type is being adopted.

        **Documentation**: https://forge.autodesk.com/en/docs/oauth/v2/reference/http/gettoken-POST

        Args:
            client_id (str): Client ID of the app.
            client_secret (str): Client secret of the app.
            code (str): The authorization code captured from the code query parameter when the user is redirected back to the callback URL.
            redirect_uri (str): Must match the redirect_uri parameter used in the `get_authorization_url`.

        Returns:
            dict: Parsed response object with properties `token_type`, `access_token`, `refresh_token`, and `expires_in`.

        Examples:
            ```
            FORGE_CLIENT_ID = os.environ["FORGE_CLIENT_ID"]
            FORGE_CLIENT_SECRET = os.environ["FORGE_CLIENT_SECRET"]
            client = AuthenticationClient()
            url = client.get_authorization_url(FORGE_CLIENT_ID, "code", "http://localhost:3000/callback", [Scope.ViewablesRead])
            # redirect the user to URL, and wait for callback to http://localhost:3000/callback
            code = '...' # extract 'code' query parameter from the callback
            auth = client.get_token(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET, code, "http://localhost:3000/callback")
            print(auth["access_token"])
            ```
        """
        form = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri
        }
        return self._post('/gettoken', form=form).json()

    def refresh_token(self, client_id: str, client_secret: str, refresh_token: str, scopes: list[Scope]) -> dict:
        """
        Acquire a new access token by using the refresh token provided by `get_token`.

        **Documentation**: https://forge.autodesk.com/en/docs/oauth/v2/reference/http/refreshtoken-POST

        Args:
            client_id (str): Client ID of the app.
            client_secret (str): Client secret of the app.
            refresh_token (str): Refresh token used to acquire a new access token.
            scopes (list[str]): List of required scopes.

        Returns:
            dict: Parsed response object with properties `token_type`, `access_token`, `refresh_token`, and `expires_in`.

        Examples:
            ```
            FORGE_CLIENT_ID = os.environ["FORGE_CLIENT_ID"]
            FORGE_CLIENT_SECRET = os.environ["FORGE_CLIENT_SECRET"]
            refresh_token = '...' # retrieve the refresh token, for example, from cookies
            client = AuthenticationClient()
            auth = client.refresh_token(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET, refresh_token, [Scope.ViewablesRead])
            print(auth["access_token"])
            ```
        """
        form = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'scope': ' '.join(map(lambda s: s.value, scopes))
        }
        return self._post('/refreshtoken', form=form).json()

    def get_user_profile(self, access_token: str) -> dict:
        """
        Get the profile information of an authorizing end user in a three-legged context.

        **Documentation**: https://forge.autodesk.com/en/docs/oauth/v2/reference/http/users-@me-GET

        Args:
            access_token (str): Token obtained via a three-legged OAuth flow.

        Returns:
            dict: Parsed response object with properties `userId`, `userName`, `emaillId`, `firstName`, `lastName`, etc.

        Examples:
            ```
            access_token = '...' # get a three-legged access token, for example, from cookies
            client = AuthenticationClient()
            info = client.get_user_profile(access_token)
            print(auth["userName"])
            ```
        """
        headers = { 'Authorization': 'Bearer {}'.format(access_token) }
        return self._get('/users/@me', headers=headers).json()

class TokenProviderInterface:
    def get_token(self, scopes: list[Scope]) -> str:
        """
        Generates access token for given set of scopes.

        Args:
            scopes (list[Scope]): List of scopes that the generated access token should support.

        Returns:
            str: Access token.
        """
        pass

class SimpleTokenProvider(TokenProviderInterface):
    """
    Simple implementation of `TokenProviderInterface` when you already have an access token that you want to use.
    When using this approach, make sure that the hard-coded access token supports all the scopes that may be needed.
    """

    def __init__(self, access_token: str):
        """
        Create new instance of the provider.

        Args:
            access_token (str): Token that will always be returned by `SimpleTokenProvider.get_token`.
        """
        self.access_token = access_token

    def get_token(self, scopes: list[Scope]) -> str:
        return self.access_token

class OAuthTokenProvider(TokenProviderInterface):
    """
    Helper class that automatically generates (and caches) access tokens using specific app credentials.
    """

    def __init__(self, client_id: str, client_secret: str):
        """
        Create new instance of the provider.

        Args:
            client_id (str): Application client ID.
            client_secret (str): Application client secret.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_client = AuthenticationClient()
        self.cache = {}

    def get_token(self, scopes: list[Scope]) -> str:
        cache_key = '+'.join(map(lambda s: s.value, scopes))
        now = datetime.now()
        if cache_key in self.cache:
            auth = self.cache[cache_key]
            if auth['expires_at'] > now:
                return auth
        auth = self.auth_client.authenticate(self.client_id, self.client_secret, scopes)
        auth['expires_at'] = now + timedelta(0, auth['expires_in'])
        return auth

class BaseOAuthClient(BaseClient):
    def __init__(self, token_provider: TokenProviderInterface, base_url: str):
        """
        Create new instance of the client.

        Args:
            token_provider (TokenProviderInterface): Provider that will be used to generate access tokens for API calls.
            base_url (str): Base URL for API calls.
        """
        BaseClient.__init__(self, base_url)
        self.token_provider = token_provider

    def _get(self, url: str, scopes: list[Scope], params: dict=None, headers: dict=None):
        if not headers:
            headers = {}
        self._set_auth_headers(headers, scopes)
        return BaseClient._get(self, url, params, headers)

    def _post(self, url: str, scopes: list[Scope], form: dict=None, json: dict=None, buff=None, params: dict=None, headers: dict=None):
        if not headers:
            headers = {}
        self._set_auth_headers(headers, scopes)
        return BaseClient._post(self, url, form, json, buff, params, headers)

    def _put(self, url: str, scopes: list[Scope], form: dict=None, json: dict=None, buff=None, params: dict=None, headers: dict=None):
        if not headers:
            headers = {}
        self._set_auth_headers(headers, scopes)
        return BaseClient._put(self, url, form, json, buff, params, headers)

    def _delete(self, url: str, scopes: list[Scope], params: dict=None, headers: dict=None):
        if not headers:
            headers = {}
        self._set_auth_headers(headers, scopes)
        return BaseClient._delete(self, url, params, headers)

    def _set_auth_headers(self, headers: dict, scopes: list[Scope]):
        if not 'Authorization' in headers:
            auth = self.token_provider.get_token(scopes)
            headers['Authorization'] = 'Bearer {}'.format(auth['access_token'])