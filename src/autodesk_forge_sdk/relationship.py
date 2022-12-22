"""
Clients for working with the Forge Data Management service.
"""
from os import path
from enum import Enum
from typing import Dict, List
from .auth import BaseOAuthClient, Scope, TokenProviderInterface

BASE_URL = "https://developer.api.autodesk.com"
RELATIONSHIPS_URL = f"{BASE_URL}/bim360/relationship/v2"
READ_SCOPES = [Scope.BUCKET_READ, Scope.DATA_READ]
WRITE_SCOPES = [Scope.BUCKET_CREATE, Scope.DATA_CREATE, Scope.DATA_WRITE]
DELETE_SCOPES = [Scope.BUCKET_DELETE]

class RelationshipManagementClient(BaseOAuthClient):
    """
    Forge Relationship management client.

    **Documentation**: https://aps.autodesk.com/en/docs/acc/v1/reference/http/relationship-service-v2-search-relationships-GET/
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
        BaseOAuthClient.__init__(self, token_provider, RELATIONSHIPS_URL)

    def _get_paginated(self, url: str, **kwargs) -> List:
        json = self._get(url, **kwargs).json()
        results = json["data"]
        while "links" in json and "next" in json["links"]:
            url = json["links"]["next"]["href"]
            json = self._get(url, **kwargs).json()
            results = results + json["data"]
        return results

    def get_relationships(self, container_id: str=None, search_params: dict = None) -> Dict:
        """
        Retrieves a list of relationships that match the provided search parameters.

        This endpoint supports filtering based on domain, entity type, and ID. The endpoint also supports the option to include deleted relationships. This search is additive for the domain -> type -> ID hierarchy.
        Deleted relationships are only returned if the includeDeleted query parameter is set to true.
        Callers also have the option to include withDomain, withType and withId to restrict the search to include relationships between domain entities. This endpoint supports the following query semantics:

        **Documentation**: https://aps.autodesk.com/en/docs/acc/v1/reference/http/relationship-service-v2-search-relationships-GET/

        Args:
            container_id (str): ID to filter the results by.

            search_params (dict, optional): Query Parameters:

                domain (string): The relationship domain to search.

                type (string): The entity type to search.

                id (string): The entity ID to search.

                createdAfter (datetime: ISO 8601): Filters the returned relationships to those created after the given time.
                
                createdBefore (datetime: ISO 8601): Filters the returned relationships to those created before the given time.
                
                withDomain (string): The WITH relationship domain to search.
                
                withType (string): The WITH entity type to search.
                
                withId (string): The WITH entity ID to search.
                
                includeDeleted (boolean): Whether or not to include deleted relationships in the search.
                
                onlyDeleted (boolean): Whether or not to only include deleted relationships in the search.
                
                pageLimit (int): The maximum number of relationships to return in a page. If not set, the default page limit is used, as determined by the server.
                
                continuationToken (string): The token indicating the start of the page. If not set, the first page is retrieved. 

        Returns:
            Dict: Parsed response JSON.

        Examples:
            ```
            THREE_LEGGED_TOKEN = os.environ["THREE_LEGGED_TOKEN"]
            client = RelationshipManagementClient(SimpleTokenProvider(THREE_LEGGED_TOKEN))
            relationships = client.get_relationships(CONATINER_ID)
            ```
        """
        enpoint = f'/containers/{container_id}/relationships:search'
        headers = { "Content-Type": "application/vnd.api+json" }

        return self._get(enpoint, scopes=READ_SCOPES, headers=headers, params=search_params).json()
