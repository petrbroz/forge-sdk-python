"""
Clients for working with the Forge Webhooks service.
"""

from typing import Dict, List
from .auth import BaseOAuthClient, Scope, TokenProviderInterface

BASE_URL = "https://developer.api.autodesk.com"
WEBHOOKS_URL = f"{BASE_URL}/webhooks/v1"
READ_SCOPES = [Scope.BUCKET_READ, Scope.DATA_READ]
WRITE_SCOPES = [Scope.BUCKET_CREATE, Scope.DATA_CREATE, Scope.DATA_WRITE]
DELETE_SCOPES = [Scope.BUCKET_DELETE]

class WebhooksClient(BaseOAuthClient):
    """
    Forge Webhooks client.

    **Documentation**: https://forge.autodesk.com/en/docs/webhooks/v1/reference/http/
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
            client = WebhooksClient(SimpleTokenProvider(THREE_LEGGED_TOKEN))
            ```
        """
        BaseOAuthClient.__init__(self, token_provider, WEBHOOKS_URL)

    def _get_paginated(self, url: str, **kwargs) -> List:
        items = []
        while url:
            json = self._get(url, **kwargs).json()
            items = items + json["data"]
            next = json["links"]["next"]
            if next is not None:
                url = next
            else:
                url = None
        return items
  
    def get_webhooks(self, region: str = None) -> Dict:
        """
        Retrieves a paginated list of all the webhooks for a specified system.
        If the pageState query string is not specified, the first page is returned.

        **Documentation**:
        https://forge.autodesk.com/en/docs/webhooks/v1/reference/http/webhooks/systems-system-events-event-hooks-hook_id-DELETE/

        Args:
            region (str, optional): Specifies the geographical location (region) of the server that the request is executed on.
            Supported values are: "US", "EMEA". Default is "US".
            pageState (str, optional): Base64 encoded string used to return the next page of the list of webhooks.
            This can be obtained from the next field of the previous page.
            PagingState instances are not portable and implementation is subject to change across versions.
            Default page size is 200.
        Returns:
            Dict: dictionary containing data on webhooks

        """
        if region is None:
            region = {}
        else:
            region = {"x-ads-region": region}

        headers = { "Content-Type": "application/json"} | region

        return self._get_paginated(f"{WEBHOOKS_URL}/systems/data/hooks",
        scopes=READ_SCOPES, headers=headers)

    def create_webhook_for_event(self, callback_url: str,  scope: dict, event: str, filter_expression: str=None, region: str = None, hookExpiry: str = None, **kwargs) -> Dict:
        """
        Add new webhook to receive the notification on a specified event.

        **Documentation**:
        https://forge.autodesk.com/en/docs/webhooks/v1/reference/http/webhooks/systems-system-events-event-hooks-POST/

        Args:
            callback_url (str, required): Callback URL registered for the webhook. Example: "http://bf067e05.ngrok.io/callback"
            scope (dict, required): An object that represents the extent to where the event is monitored. For example, if the scope is folder, the webhooks service generates a notification for the specified event occurring in any sub folder or item within that folder. example: {"folder": "urn:adsk.wipprod:fs.folder:co.wT5lCWlXSKeo3razOfHJAw"}.
            event (str, required): Type of event. example: "dm.version.added"
            filter_expression (str, optional): JsonPath expression that can be used by you to filter the callbacks you receive. Example: "$[?(@.ext in ['.docx','.csv']]"
            region (str, optional): Specifies the geographical location (region) of the server that the request is executed on. Supported values are: "US", "EMEA". Default is "US".
            hookExpiry (str, optional): Optional. ISO8601 formatted date and time when the hook should expire and automatically be deleted. Not providing this parameter means the hook never expires. Example: "2023-06-14T17:04:10.444Z"

        Returns:
            Dict: code 201 for success

        """
        headers = { "Content-Type": "application/vnd.api+json", "x-ads-region": region }

        data = {
            "callbackUrl": callback_url,
            "scope": scope,
            'filter': filter_expression,
            "hookExpiry": hookExpiry
          } | kwargs
    

        return self._post(f"{WEBHOOKS_URL}/systems/data/events/{event}/hooks",
        scopes=READ_SCOPES, headers=headers, json=data).json()
    
    def delete_webhook_for_event(self, event: str, hook_id: str, region: str = None) -> Dict:
        """
        Deletes a webhook based on webhook ID

        **Documentation**:
        https://forge.autodesk.com/en/docs/webhooks/v1/reference/http/webhooks/systems-system-events-event-hooks-hook_id-DELETE/

        Args:
            event (str, required): Type of event. example: "dm.version.added"
            hook_id (str, required): Webhook ID to delete
            region (str, optional): Specifies the geographical location (region) of the server that the request is executed on. Supported values are: "US", "EMEA". Default is "US".
        Returns:
            Dict: code 204 for success

        """
        headers = { "Content-Type": "application/vnd.api+json", "x-ads-region": region }

        return self._delete(f"{WEBHOOKS_URL}/systems/data/events/{event}/hooks/{hook_id}",
        scopes=READ_SCOPES, headers=headers).json()
