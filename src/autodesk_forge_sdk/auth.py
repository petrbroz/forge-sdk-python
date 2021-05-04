import requests
from datetime import datetime, timedelta
from urllib.parse import quote
from .base import BaseClient

BASE_URL = 'https://developer.api.autodesk.com/authentication/v1'

class AuthenticationClient(BaseClient):
    """
    Forge Authentication service client.

    For more details, see https://forge.autodesk.com/en/docs/oauth/v2/reference/http.
    """

    def __init__(self, base_url=BASE_URL):
        BaseClient.__init__(self, base_url)

    def authenticate(self, client_id, client_secret, scopes):
        """Get a two-legged access token by providing your app’s client ID and secret.

        Parameters:
        client_id (string): Client ID of the app.
        client_secret (string): Client secret of the app.
        scopes (list): List of required scopes.

        Returns:
        object: Parsed response object with properties 'token_type', 'access_token', and 'expires_in'.
        """
        form = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials',
            'scope': ' '.join(scopes)
        }
        return self._post('/authenticate', form=form).json()

    def get_authorization_url(self, client_id, response_type, redirect_uri, scopes, state=None):
        """Generate a URL to redirect an end user to
        in order to acquire the user’s consent for your app to access the specified resources.

        Parameters:
        client_id (string): Client ID of the app.
        response_type (string): Must be either 'code' for authorization code grant flow or 'token' for implicit grant flow.
        redirect_uri (string): URL-encoded callback URL that the end user will be redirected to after completing the authorization flow.
        scopes (list): List of required scopes.
        state (string): Optional payload containing arbitrary data that the authentication flow will pass back verbatim in a state query parameter to the callback URL.

        Returns:
        string: Complete authorization URL.
        """
        url = 'https://developer.api.autodesk.com/authentication/v1/authorize'
        url = url + '?client_id={}'.format(quote(client_id))
        url = url + '&response_type={}'.format(response_type)
        url = url + '&redirect_uri={}'.format(quote(redirect_uri))
        url = url + '&scope={}'.format(quote(' '.join(scopes)))
        if state:
            url += '&state={}'.format(quote(state))
        return url

    def get_token(self, client_id, client_secret, code, redirect_uri):
        """Exchange an authorization code extracted from a 'GET authorize' callback
        for a three-legged access token. This API will only be used when the 'Authorization Code' grant type
        is being adopted.

        Parameters:
        client_id (string): Client ID of the app.
        client_secret (string): Client secret of the app.
        code (string): The authorization code captured from the code query parameter when the 'GET authorize' redirected back to the callback URL.
        redirect_uri (string): Must match the redirect_uri parameter used in 'GET authorize'.

        Returns:
        object: Parsed response object with properties 'token_type', 'access_token', 'refresh_token', and 'expires_in'.
        """
        form = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri
        }
        return self._post('/gettoken', form=form).json()

    def refresh_token(self, client_id, client_secret, refresh_token, scopes):
        """Acquire a new access token by using the refresh token provided by the `POST gettoken` endpoint.

        Parameters:
        client_id (string): Client ID of the app.
        client_secret (string): Client secret of the app.
        refresh_token (string): The refresh token used to acquire a new access token.
        scopes (list): List of required scopes.

        Returns:
        object: Parsed response object with properties 'token_type', 'access_token', 'refresh_token', and 'expires_in'.
        """
        form = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'scope': ' '.join(scopes)
        }
        return self._post('/refreshtoken', form=form).json()

    def get_profile(self, access_token):
        """Get the profile information of an authorizing end user in a three-legged context.

        Parameters:
        access_token (string): Token obtained via a three-legged OAuth flow.

        Returns:
        object: Parsed response object with properties 'userId', 'userName', 'emaillId', 'firstName', 'lastName', etc.
        """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self._get('/users/@me', headers=headers).json()

class PassiveTokenProvider:
    def __init__(self, token):
        self.token = token
    def get_token(self, scopes):
        return self.token

class ActiveTokenProvider:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_client = AuthenticationClient()
        self.cache = {}
    def get_token(self, scopes):
        cache_key = '+'.join(scopes)
        now = datetime.now()
        if cache_key in self.cache:
            auth = self.cache[cache_key]
            if auth['expires_at'] > now:
                return auth
        auth = self.auth_client.authenticate(self.client_id, self.client_secret, scopes)
        auth['expires_at'] = now + timedelta(0, auth['expires_in'])
        return auth

class BaseOAuthClient(BaseClient):
    def __init__(self, token_provider, base_url):
        BaseClient.__init__(self, base_url)
        self.token_provider = token_provider

    def _get(self, url, scopes, params=None, headers=None):
        if not headers:
            headers = {}
        self._set_auth_headers(headers, scopes)
        return BaseClient._get(self, url, params, headers)

    def _post(self, url, scopes, form=None, json=None, buff=None, params=None, headers=None):
        if not headers:
            headers = {}
        self._set_auth_headers(headers, scopes)
        return BaseClient._post(self, url, form, json, buff, params, headers)

    def _put(self, url, scopes, form=None, json=None, buff=None, params=None, headers=None):
        if not headers:
            headers = {}
        self._set_auth_headers(headers, scopes)
        return BaseClient._put(self, url, form, json, buff, params, headers)

    def _delete(self, url, scopes, params=None, headers=None):
        if not headers:
            headers = {}
        self._set_auth_headers(headers, scopes)
        return BaseClient._delete(self, url, params, headers)

    def _set_auth_headers(self, headers, scopes):
        if not 'Authorization' in headers:
            auth = self.token_provider.get_token(scopes)
            headers['Authorization'] = 'Bearer {}'.format(auth['access_token'])