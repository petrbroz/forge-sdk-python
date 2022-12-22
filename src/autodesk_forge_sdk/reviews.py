"""
Clients for working with the Reviews service.
"""

from typing import Dict, List
from .auth import BaseOAuthClient, Scope, TokenProviderInterface

BASE_URL = "https://developer.api.autodesk.com"
WEBHOOKS_URL = f"{BASE_URL}/dm/v2"
READ_SCOPES = [Scope.BUCKET_READ, Scope.DATA_READ]
WRITE_SCOPES = [Scope.BUCKET_CREATE, Scope.DATA_CREATE, Scope.DATA_WRITE]
DELETE_SCOPES = [Scope.BUCKET_DELETE]

class ReviewsClient(BaseOAuthClient):
    """
    Reviews client.

    **Documentation**: No official documentation as of 2022-12-22. The endpoints has been found at acc.autodesk.com
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

            base_url (str, optional): Base URL for API calls.

        Examples:
            ```
            THREE_LEGGED_TOKEN = os.environ["THREE_LEGGED_TOKEN"]
            client = ReviewsClient(SimpleTokenProvider(THREE_LEGGED_TOKEN))
            ```
        """
        BaseOAuthClient.__init__(self, token_provider, WEBHOOKS_URL)

    def _get_paginated(self, url: str, **kwargs) -> List:
        items = []
        while url:
            json = self._get(url, **kwargs).json()
            items = items + json["results"]
            next_page = json["pagination"]["next"]
            if next_page not in [None,'']:
                url = next_page
                raise 'Not implemented'
            else:
                url = None
        return items
  
    def get_reviews(self, project_id: str) -> Dict:
        """
        intro

        **Documentation**:
        https://??

        Args:
            project_id (str)
        Returns:
            Dict: dictionary containing data on webhooks

        """
    
        headers = { "Content-Type": "application/json"}

        endpoint = f'/projects/{project_id}/reviews?sort=-sequenceId&offset=0&limit=20'

        return self._get_paginated(endpoint,
        scopes=READ_SCOPES, headers=headers)

    def get_review(self, project_id: str, review_id: str) -> Dict:
        """
        intro

        **Documentation**:
        https://??

        Args:
            project_id (str)
        Returns:
            Dict: dictionary containing data on webhooks

        """
    
        headers = { "Content-Type": "application/json"}

        endpoint = f'/projects/{project_id}/reviews/{review_id}/versions?limit=50&offset=0'

        return self._get_paginated(endpoint,
        scopes=READ_SCOPES, headers=headers)
