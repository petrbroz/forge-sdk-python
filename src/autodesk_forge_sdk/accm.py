"""
Clients for working with the Forge Account Admin Management service.
"""
# from os import path
# from enum import Enum
from typing import List, Dict
from .auth import BaseOAuthClient, Scope, TokenProviderInterface

BASE_URL = "https://developer.api.autodesk.com"
ACCOUNT_MANAGEMENT_URL = f"{BASE_URL}/hq/v1"
ACCOUNT_MANAGEMENT_URL_V2 = f"{BASE_URL}/hq/v2"
ACCOUNT_MANAGEMENT_URL_BIM360 = f"{BASE_URL}/bim360/admin/v1"
READ_SCOPES = [Scope.BUCKET_READ, Scope.DATA_READ, Scope.ACCOUNT_READ]
WRITE_SCOPES = [Scope.BUCKET_CREATE, Scope.DATA_CREATE, Scope.DATA_WRITE]
DELETE_SCOPES = [Scope.BUCKET_DELETE]

class AccountManagementClient(BaseOAuthClient):
    """
    Forge Account Management client.

    **Documentation**: https://forge.autodesk.com/en/docs/acc/v1/overview/introduction/
    """

    def __init__(
        self, token_provider: TokenProviderInterface):
        """
        Create new instance of the client.

        Args:
            token_provider (autodesk_forge_sdk.auth.TokenProviderInterface):
                Provider that will be used to generate access tokens for API calls.

                Use `autodesk_forge_sdk.auth.OAuthTokenProvider` if you have your app's client ID
                and client secret available, `autodesk_forge_sdk.auth.SimpleTokenProvider`
                if you would like to use an existing access token instead, or even your own
                implementation of the `autodesk_forge_sdk.auth.TokenProviderInterface` interface.

                Note that many APIs in the Forge Data Management service require
                a three-legged OAuth token.
            base_url (str, optional): Base URL for API calls.

        Examples:
            ```
            THREE_LEGGED_TOKEN = os.environ["THREE_LEGGED_TOKEN"]
            client = DataManagementClient(SimpleTokenProvider(THREE_LEGGED_TOKEN))
            ```
        """
        BaseOAuthClient.__init__(self, token_provider, ACCOUNT_MANAGEMENT_URL)

    def _get_paginated(self, url: str, **kwargs) -> List:
        limit = 100 # lowest max limit for all endpoints seems to be 100.
        items = []
        offset = 0

        while url:

            url_pagination = f"{url}?offset={offset}&limit={limit}"
            json = self._get(url_pagination, **kwargs).json()

            items += json

            # if number of returned objects is equal to the limit, there might be more objects to get.
            if len(json) == limit:
                offset += limit

            else:
                url = None

        return items

    
    def get_users(self, account_id: str, user_id: str = None) -> Dict:
        """
        If user_id is provided: Query the details of a specific user.
        If no user_id is provided: Query all the users in a specific ACC or BIM 360 account.
        ! Note: search not implemented https://forge.autodesk.com/en/docs/acc/v1/reference/http/users-search-GET/

        **Documentation**: https://forge.autodesk.com/en/docs/acc/v1/reference/http/users-:user_id-GET/
        https://forge.autodesk.com/en/docs/acc/v1/reference/http/users-GET/

        Args:
            account_id (str): The account ID of the user. This corresponds to hub ID in the Data Management API. To convert a hub ID into an account ID you need to remove the “b.” prefix. For example, a hub ID of b.c8b0c73d-3ae9 translates to an account ID of c8b0c73d-3ae9.
            user_id (str, optional): User ID.

        Returns:
            List(Dict): Dictionary parsed from the response JSON.

        Examples:
            ```
            # TODO: write
            ```
        """

        if user_id:

            url = f"/accounts/{account_id}/users/{user_id}"

        else:

            url = f"/accounts/{account_id}/users"

        headers = { "Content-Type": "application/vnd.api+json" }

        return self._get(url,
            scopes=READ_SCOPES, headers=headers).json()

    def search_companies(self, account_id: str, name: str, **kwargs) -> Dict:
        """
        Query all the companies with matching name.

        **Documentation**: https://forge.autodesk.com/en/docs/acc/v1/reference/http/companies-search-GET/

        Args:
            account_id (str): The account ID of the company. This corresponds to hub ID in the Data
            Management API. To convert a hub ID into an account ID you need to remove the “b.”
            prefix. For example, a hub ID of b.c8b0c73d-3ae9 translates to an account ID of c8b0c73d-3ae9.
            name (str): Company name.
            **kwargs

        Returns:
            List(Dict): Dictionary parsed from the response JSON.

        Examples:
            ```
            # TODO: write
            ```
        """

        url = f"/accounts/{account_id}/companies/search?name={name}"

        params = {'name': name}

        if kwargs: # TODO: test if this works
            params.update(kwargs)

        headers = { "Content-Type": "application/vnd.api+json" }

        return self._get(url,
            scopes=READ_SCOPES, headers=headers,
            params=params).json()
    
    def get_companies(self, account_id: str) -> List:
        """
        Query all the partner companies in a specific BIM 360 or ACC account.

        **Documentation**: https://forge.autodesk.com/en/docs/acc/v1/reference/http/companies-GET/

        Args:
            account_id (str): The account ID of the user. This corresponds to hub ID in the Data Management API. To convert a hub ID into an account ID you need to remove the “b.” prefix. For example, a hub ID of b.c8b0c73d-3ae9 translates to an account ID of c8b0c73d-3ae9.

        Returns:
            List(Dict): List of dictionary parsed from the response JSON.

        Examples:
            ```
            from autodesk_forge_sdk import DataManagementClient

            datam_client = DataManagementClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
            companies = accm_client.get_companies('account_id')
            ```
        """
        url = f'/accounts/{account_id}/companies'
        headers = { "Content-Type": "application/vnd.api+json" }

        return self._get_paginated(url,
            scopes=READ_SCOPES, headers=headers)

    def get_industry_roles(self, account_id: str, project_id: str) -> List:
        """
        Retrieves the industry roles for the project. For example, contractor and architect.

        **Documentation**: https://forge.autodesk.com/en/docs/bim360/v1/reference/http/projects-project_id-industry_roles-GET/

        Args:
            account_id (str): The account ID of the user. This corresponds to hub ID in the Data Management API. To convert a hub ID into an account ID you need to remove the “b.” prefix. For example, a hub ID of b.c8b0c73d-3ae9 translates to an account ID of c8b0c73d-3ae9.
            project_id (str): The project ID. This corresponds to project ID in the Data Management API. To convert a project ID in the Data Management API into a project ID in the BIM 360 API you need to remove the “b.” prefix. For example, a project ID of b.a4be0c34a-4ab7 translates to a project ID of a4be0c34a-4ab7.

        Returns:
            List(Dict): List of dictionary parsed from the response JSON.

        Examples:
            ```
            from autodesk_forge_sdk import AccountManagementClient

            accm_client = AccountManagementClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
            industry_roles = self.accm_client.get_industry_roles('account_id', 'project_id')
            ```
        """
        url = f'{ACCOUNT_MANAGEMENT_URL_V2}/accounts/{account_id}/projects/{project_id}/industry_roles'
        headers = { "Content-Type": "application/vnd.api+json" }

        return self._get(url,
            scopes=READ_SCOPES, headers=headers).json()

class AccountManagementClient_BIM360(BaseOAuthClient):
    """
    Forge Account Management client.

    **Documentation**: https://forge.autodesk.com/en/docs/acc/v1/overview/introduction/
    """

    def __init__(
        self, token_provider: TokenProviderInterface):
        """
        Create new instance of the client.

        Args:
            token_provider (autodesk_forge_sdk.auth.TokenProviderInterface):
                Provider that will be used to generate access tokens for API calls.

                Use `autodesk_forge_sdk.auth.OAuthTokenProvider` if you have your app's client ID
                and client secret available, `autodesk_forge_sdk.auth.SimpleTokenProvider`
                if you would like to use an existing access token instead, or even your own
                implementation of the `autodesk_forge_sdk.auth.TokenProviderInterface` interface.

                Note that many APIs in the Forge Data Management service require
                a three-legged OAuth token.
            base_url (str, optional): Base URL for API calls.

        Examples:
            ```
            THREE_LEGGED_TOKEN = os.environ["THREE_LEGGED_TOKEN"]
            client = DataManagementClient(SimpleTokenProvider(THREE_LEGGED_TOKEN))
            ```
        """
        BaseOAuthClient.__init__(self, token_provider, ACCOUNT_MANAGEMENT_URL_BIM360)

    def _get_paginated(self, url: str, **kwargs) -> List:
        limit = 100 # lowest max limit for all endpoints seems to be 100.
        items = []
        offset = 0

        while url:

            url_pagination = f"{url}?offset={offset}&limit={limit}"
            json = self._get(url_pagination, **kwargs).json()
   
            total_results = json["pagination"]["totalResults"]

            items += json["results"]

            if (total_results > limit) and (total_results - offset > 0):
                offset += limit
            
            else:
                url = None

        return items

    def get_project_users(self, project_id: str) -> Dict:
        """
        Retrieves information about all the users in a project.

        **Documentation**: https://forge.autodesk.com/en/docs/bim360/v1/reference/http/admin-v1-projects-projectId-users-GET/

        Args:
            project_id (str): The project ID. This corresponds to project ID in the Data Management API. To convert a project ID in the Data Management API into a project ID in the BIM 360 API you need to remove the “b.” prefix.

        Returns:
            List(Dict): Dictionary parsed from the response JSON.

        Examples:
            ```
            from autodesk_forge_sdk import AccountManagementClient
            
            accm_client = AccountManagementClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
            users = accm_client.get_project_users('project_id')
            ```
        """

        url = f"/projects/{project_id}/users"

        headers = { "Content-Type": "application/vnd.api+json" }

        return self._get_paginated(url,
            scopes=READ_SCOPES, headers=headers)
