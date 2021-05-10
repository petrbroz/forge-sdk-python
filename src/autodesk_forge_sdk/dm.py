"""
Clients for working with the Forge Data Management service.
"""

from enum import Enum
from urllib.parse import quote
from .auth import BaseOAuthClient, Scope, TokenProviderInterface

OSS_BASE_URL = "https://developer.api.autodesk.com/oss/v2"
DATA_MANAGEMENT_BASE_URL = "https://developer.api.autodesk.com/project/v1"
READ_SCOPES = [Scope.BUCKET_READ, Scope.DATA_READ]
WRITE_SCOPES = [Scope.BUCKET_CREATE, Scope.DATA_CREATE, Scope.DATA_WRITE]
DELETE_SCOPES = [Scope.BUCKET_DELETE]


class DataRetention(Enum):
    """
    Data retention policies.
    """
    TRANSIENT = "transient"
    """
    Think of this type of storage as a cache. Use it for ephemeral results. For example,
    you might use this for objects that are part of producing other persistent artifacts,
    but otherwise are not required to be available later.

    Objects older than 24 hours are removed automatically. Each upload of an object
    is considered unique, so, for example, if the same rendering is uploaded multiple times,
    each of them will have its own retention period of 24 hours.
    """
    TEMPORARY = "temporary"
    """
    This type of storage is suitable for artifacts produced for user-uploaded content
    where after some period of activity, the user may rarely access the artifacts.

    When an object has reached 30 days of age, it is deleted.
    """
    PERSISTENT = "persistent"
    """
    Persistent storage is intended for user data. When a file is uploaded,
    the owner should expect this item to be available for as long as the owner account is active,
    or until he or she deletes the item.
    """


class OSSClient(BaseOAuthClient):
    """
    Forge Data Management object storage client.

    **Documentation**: https://forge.autodesk.com/en/docs/data/v2/reference/http
    """

    def __init__(self, token_provider: TokenProviderInterface(), base_url: str=OSS_BASE_URL):
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
            client1 = OSSClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))

            FORGE_ACCESS_TOKEN = os.environ["FORGE_ACCESS_TOKEN"]
            client2 = OSSClient(SimpleTokenProvider(FORGE_ACCESS_TOKEN))

            class MyTokenProvider(autodesk_forge_sdk.auth.TokenProviderInterface):
                def get_token(self, scopes):
                    return "your own access token retrieved from wherever"
            client3 = OSSClient(MyTokenProvider())
            ```
        """
        BaseOAuthClient.__init__(self, token_provider, base_url)

    def _get_paginated(self, url: str, **kwargs) -> list:
        items = []
        while url:
            json = self._get(url, **kwargs).json()
            items = items + json["items"]
            if "next" in json:
                url = json["next"]
            else:
                url = None
        return items

    def get_buckets(self, region: str = None, limit: int = None, start_at: str = None) -> dict:
        """
        List buckets owned by the application, using pagination.

        **Documentation**: https://forge.autodesk.com/en/docs/data/v2/reference/http/buckets-GET

        Args:
            region (str, optional): Region where the bucket resides.
                Acceptable values: US, EMEA. Default: US.
            limit (int, optional): Limit to the response size.
                Acceptable values: 1-100. Default = 10.
            start_at (str, optional): Key to use as an offset to continue pagination.
                This is typically the last bucket key found in a preceding `get_buckets` response.

        Returns:
            dict: Parsed response object with top-level properties `items` and `next`.

        Examples:
            ```
            FORGE_CLIENT_ID = os.environ["FORGE_CLIENT_ID"]
            FORGE_CLIENT_SECRET = os.environ["FORGE_CLIENT_SECRET"]
            client = OSSClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
            buckets = client.get_buckets(limit=8)
            print(buckets.items)
            print(buckets.next)
            ```
        """
        params = {}
        if region:
            params["region"] = region
        if limit:
            params["limit"] = limit
        if start_at:
            params["startAt"] = start_at
        return self._get("/buckets", scopes=READ_SCOPES, params=params).json()

    def get_all_buckets(self, region: str = None) -> list:
        """
        List all buckets owned by the application. Similar to `OSSClient.get_buckets`
        but returning all results without pagination.

        **Documentation**: https://forge.autodesk.com/en/docs/data/v2/reference/http/buckets-GET

        Args:
            region (str, optional): Region where the bucket resides.
                Acceptable values: US, EMEA. Default: US.

        Returns:
            list[dict]: List of objects representing individual buckets.

        Examples:
            ```
            FORGE_CLIENT_ID = os.environ["FORGE_CLIENT_ID"]
            FORGE_CLIENT_SECRET = os.environ["FORGE_CLIENT_SECRET"]
            client = OSSClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
            buckets = client.get_all_buckets()
            print(buckets)
            ```
        """
        params = {}
        if region:
            params["region"] = region
        return self._get_paginated("/buckets", scopes=READ_SCOPES, params=params)

    def get_bucket_details(self, bucket_key: str) -> dict:
        """
        Get bucket details in JSON format if the caller is the owner of the bucket.
        A request by any other application will result in a response of 403 Forbidden.

        **Documentation**:
            https://forge.autodesk.com/en/docs/data/v2/reference/http/buckets-:bucketKey-details-GET

        Returns:
            dict: Parsed response JSON.

        Examples:
            ```
            FORGE_CLIENT_ID = os.environ["FORGE_CLIENT_ID"]
            FORGE_CLIENT_SECRET = os.environ["FORGE_CLIENT_SECRET"]
            FORGE_BUCKET = os.environ["FORGE_BUCKET"]
            client = OSSClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
            details = client.get_bucket_details(FORGE_BUCKET)
            print(details)
            ```
        """
        endpoint = "/buckets/{}/details".format(quote(bucket_key))
        return self._get(endpoint, scopes=READ_SCOPES).json()

    def create_bucket(
        self, bucket_key: str, data_retention_policy: DataRetention, region: str
    ) -> dict:
        """
        Create a bucket. Buckets are arbitrary spaces that are created by applications
        and are used to store objects for later retrieval. A bucket is owned by the application
        that creates it.

        **Documentation**: https://forge.autodesk.com/en/docs/data/v2/reference/http/buckets-POST

        Args:
            bucket_key (str): A unique name you assign to a bucket. It must be globally unique
                across all applications and regions, otherwise the call will fail.
                Possible values: -_.a-z0-9 (between 3-128 characters in length).
                Note that you cannot change a bucket key.
            data_retention_policy (DataRetention): Data retention policy.
            region (str): The region where the bucket resides. Acceptable values: US, EMEA.

        Returns:
            dict: Parsed response JSON.

        Examples:
            ```
            FORGE_CLIENT_ID = os.environ["FORGE_CLIENT_ID"]
            FORGE_CLIENT_SECRET = os.environ["FORGE_CLIENT_SECRET"]
            FORGE_BUCKET = os.environ["FORGE_BUCKET"]
            client = OSSClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
            details = client.create_bucket(FORGE_BUCKET, DataRetention.TEMPORARY, "US")
            print(details)
            ```
        """
        json = {
            "bucketKey": bucket_key,
            "policyKey": data_retention_policy.value
        }
        headers = {
            "x-ads-region": region
        }
        return self._post("/buckets", WRITE_SCOPES, json=json, headers=headers).json()

    def delete_bucket(self, bucket_key: str):
        """
        Delete a bucket. The bucket must be owned by the application.

        **Documentation**:
            https://forge.autodesk.com/en/docs/data/v2/reference/http/buckets-:bucketKey-DELETE

        Args:
            bucket_key (str): Name of the bucket to be deleted.
        """
        endpoint = "/buckets/{}".format(quote(bucket_key))
        self._delete(endpoint, scopes=DELETE_SCOPES)

    def get_objects(self, bucket_key: str, **kwargs) -> dict:
        """
        List objects in bucket, using pagination. It is only available to the bucket creator.

        **Documentation**:
            https://forge.autodesk.com/en/docs/data/v2/reference/http/buckets-:bucketKey-objects-GET

        Args:
            bucket_key (str): Bucket key for which to get details.
            limit (int, optional): Number of objects to return in the result set.
                Acceptable values = 1 - 100. Default = 10.
            begins_with (str, optional): String to filter the result set by. The result set
                is restricted to items whose objectKey begins with the provided string.
            start_at (str, optional): Position to start listing the result set.

        Returns:
            dict: Parsed response object with top-level properties `items` and `next`.

        Examples:
            ```
            FORGE_CLIENT_ID = os.environ["FORGE_CLIENT_ID"]
            FORGE_CLIENT_SECRET = os.environ["FORGE_CLIENT_SECRET"]
            FORGE_BUCKET = os.environ["FORGE_BUCKET"]
            client = OSSClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
            objects = client.get_objects(FORGE_BUCKET, limit=8)
            print(objects.items)
            print(objects.next)
            ```
        """
        params = {}
        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]
        if "begins_with" in kwargs:
            params["beginsWith"] = kwargs["begins_with"]
        if "start_at" in kwargs:
            params["startAt"] = kwargs["start_at"]
        endpoint = "/buckets/{}/objects".format(quote(bucket_key))
        return self._get(endpoint, scopes=READ_SCOPES, params=params).json()

    def get_all_objects(self, bucket_key: str, begins_with: str = None) -> list:
        """
        List all objects in bucket. Similar to `OSSClient.get_objects` but returning
        all results without pagination.

        Args:
            begins_with (str, optional): String to filter the result set by. The result set
                is restricted to items whose objectKey begins with the provided string.

        Returns:
            list[dict]: List of objects.

        Examples:
            ```
            FORGE_CLIENT_ID = os.environ["FORGE_CLIENT_ID"]
            FORGE_CLIENT_SECRET = os.environ["FORGE_CLIENT_SECRET"]
            FORGE_BUCKET = os.environ["FORGE_BUCKET"]
            client = OSSClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
            objects = client.get_all_objects(FORGE_BUCKET, begins_with="prefix")
            print(objects)
            ```
        """
        params = {}
        if begins_with:
            params["beginsWith"] = begins_with
        endpoint = "/buckets/{}/objects".format(quote(bucket_key))
        return self._get_paginated(endpoint, scopes=READ_SCOPES, params=params)

    def get_object_details(self, bucket_key: str, object_key: str) -> dict:
        """
        Get object details in JSON format.

        **Documentation**:
            https://forge.autodesk.com/en/docs/data/v2/reference/http/buckets-:bucketKey-objects-:objectName-details-GET

        Args:
            bucket_key (str): Bucket key.
            object_key (str): Object name to get details for.

        Returns:
            dict: Parsed response JSON with object properties.

        Examples:
            ```
            FORGE_CLIENT_ID = os.environ["FORGE_CLIENT_ID"]
            FORGE_CLIENT_SECRET = os.environ["FORGE_CLIENT_SECRET"]
            FORGE_BUCKET = os.environ["FORGE_BUCKET"]
            client = OSSClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
            details = client.get_object_details(FORGE_BUCKET, "design.dwg")
            print(details)
            ```
        """
        endpoint = "/buckets/{}/objects/{}".format(quote(bucket_key), quote(object_key))
        return self._get(endpoint, scopes=READ_SCOPES).json()

    def upload_object(self, bucket_key: str, object_key: str, buff) -> list:
        """
        Upload an object. If the specified object name already exists in the bucket,
        the uploaded content will overwrite the existing content for the bucket name/object
        name combination.

        **Documentation**:
            https://forge.autodesk.com/en/docs/data/v2/reference/http/buckets-:bucketKey-objects-:objectName-PUT

        Args:
            bucket_key (str): Bucket key.
            object_key (str): Name of the object to be created.
            buff (list of bytes or file): Content to upload.

        Returns:
            dict: Parsed response JSON with object properties.

        Examples:
            ```
            FORGE_CLIENT_ID = os.environ["FORGE_CLIENT_ID"]
            FORGE_CLIENT_SECRET = os.environ["FORGE_CLIENT_SECRET"]
            FORGE_BUCKET = os.environ["FORGE_BUCKET"]
            client = OSSClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
            buff = bytes("This is a test...", "utf-8")
            obj1 = client.upload_object(FORGE_BUCKET, "myfile.txt", buff)
            print(obj1)
            with open("local.dwg", "rb") as file:
                obj2 = client.upload_object(FORGE_BUCKET, "mydesign.dwg", file)
                print(obj2)
            ```
        """
        endpoint = "/buckets/{}/objects/{}".format(quote(bucket_key), quote(object_key))
        return self._put(endpoint, buff=buff, scopes=WRITE_SCOPES).json()

    def delete_object(self, bucket_key: str, object_key: str):
        """
        Delete an object from bucket.

        **Documentation**:
            https://forge.autodesk.com/en/docs/data/v2/reference/http/buckets-:bucketKey-objects-:objectName-DELETE

        Args:
            bucket_key (str): Bucket key.
            object_key (str): Name of the object to be removed.
        """
        endpoint = "/buckets/{}/objects/{}".format(quote(bucket_key), quote(object_key))
        self._delete(endpoint, scopes=DELETE_SCOPES)


class DataManagementClient(BaseOAuthClient):
    """
    Forge Data Management data management client.

    **Documentation**: https://forge.autodesk.com/en/docs/data/v2/reference/http
    """

    def __init__(
        self, token_provider: TokenProviderInterface, base_url: str=DATA_MANAGEMENT_BASE_URL):
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
        BaseOAuthClient.__init__(self, token_provider, base_url)

    def _get_paginated(self, url: str, **kwargs) -> list:
        json = self._get(url, **kwargs).json()
        results = json["data"]
        while "links" in json and "next" in json["links"]:
            url = json["links"]["next"]["href"]
            json = self._get(url, **kwargs).json()
            results = results + json["data"]
        return results

    def get_hubs(self, filter_id: str=None, filter_name: str=None) -> dict:
        """
        Return a collection of accessible hubs for this member.

        Hubs represent BIM 360 Team hubs, Fusion Team hubs (formerly known as A360 Team hubs),
        A360 Personal hubs, or BIM 360 Docs accounts. Team hubs include BIM 360 Team hubs
        and Fusion Team hubs (formerly known as A360 Team hubs). Personal hubs include
        A360 Personal hubs. Only active hubs are listed.

        Note that for BIM 360 Docs, a hub ID corresponds to an account ID in the BIM 360 API.
        To convert an account ID into a hub ID you need to add a “b.” prefix. For example,
        an account ID of c8b0c73d-3ae9 translates to a hub ID of b.c8b0c73d-3ae9.

        **Documentation**: https://forge.autodesk.com/en/docs/data/v2/reference/http/hubs-GET

        Args:
            filter_id (str, optional): ID to filter the results by.
            filter_name (str, optional): Name to filter the results by.

        Returns:
            dict: Parsed response JSON.

        Examples:
            ```
            THREE_LEGGED_TOKEN = os.environ["THREE_LEGGED_TOKEN"]
            client = DataManagementClient(SimpleTokenProvider(THREE_LEGGED_TOKEN))
            response = client.get_hubs()
            print(response.data)
            print(response.links)
            ```
        """
        headers = { "Content-Type": "application/vnd.api+json" }
        params = {}
        if filter_id:
            params["filter[id]"] = filter_id
        if filter_name:
            params["filter[name]"] = filter_name
        return self._get("/hubs", scopes=READ_SCOPES, headers=headers, params=params).json()

    def get_all_hubs(self, filter_id: str=None, filter_name: str=None) -> dict:
        """
        Similar to `get_hubs`, but retrieving all hubs without pagination.

        **Documentation**: https://forge.autodesk.com/en/docs/data/v2/reference/http/hubs-GET

        Args:
            filter_id (str, optional): ID to filter the results by.
            filter_name (str, optional): Name to filter the results by.

        Returns:
            list(dict): List of hubs parsed from the response JSON.

        Examples:
            ```
            THREE_LEGGED_TOKEN = os.environ["THREE_LEGGED_TOKEN"]
            client = DataManagementClient(SimpleTokenProvider(THREE_LEGGED_TOKEN))
            hubs = client.get_all_hubs()
            print(hubs)
            ```
        """
        headers = { "Content-Type": "application/vnd.api+json" }
        params = {}
        if filter_id:
            params["filter[id]"] = filter_id
        if filter_name:
            params["filter[name]"] = filter_name
        return self._get_paginated("/hubs", scopes=READ_SCOPES, headers=headers, params=params)

    def get_projects(
        self, hub_id: str, filter_id: str=None, page_number: int=None, page_limit=None) -> dict:
        """
        Return a collection of projects for a given hub_id. A project represents a BIM 360
        Team project, a Fusion Team project, a BIM 360 Docs project, or an A360 Personal project.
        Multiple projects can be created within a single hub. Only active projects are listed.

        Note that for BIM 360 Docs, a hub ID corresponds to an account ID in the BIM 360 API.
        To convert an account ID into a hub ID you need to add a “b.” prefix. For example,
        an account ID of c8b0c73d-3ae9 translates to a hub ID of b.c8b0c73d-3ae9.

        Similarly, for BIM 360 Docs, the project ID in the Data Management API corresponds
        to the project ID in the BIM 360 API. To convert a project ID in the BIM 360 API
        into a project ID in the Data Management API you need to add a “b.” prefix. For example,
        a project ID of c8b0c73d-3ae9 translates to a project ID of b.c8b0c73d-3ae9.

        **Documentation**:
            https://forge.autodesk.com/en/docs/data/v2/reference/http/hubs-hub_id-projects-GET

        Args:
            hub_id (str): ID of a hub to list the projects for.
            filter_id (str, optional): ID to filter projects by.
            page_number (int, optional): Specifies what page to return.
                Page numbers are 0-based (the first page is page 0).
            page_limit (int, optional): Specifies the maximum number of elements
                to return in the page. The default value is 200. The min value is 1.
                The max value is 200.

        Returns:
            dict: Parsed response JSON.

        Examples:
            ```
            THREE_LEGGED_TOKEN = os.environ["THREE_LEGGED_TOKEN"]
            client = DataManagementClient(SimpleTokenProvider(THREE_LEGGED_TOKEN))
            response = client.get_projects("some-hub-id")
            print(response.data)
            print(response.links)
            ```
        """
        headers = { "Content-Type": "application/vnd.api+json" }
        params = {}
        if filter_id:
            params["filter[id]"] = filter_id
        if page_number:
            params["page[number]"] = page_number
        if page_limit:
            params["page[limit]"] = page_limit
        endpoint = "/hubs/{}/projects".format(hub_id)
        return self._get(endpoint, scopes=READ_SCOPES, headers=headers, params=params).json()

    def get_all_projects(self, hub_id: str, filter_id: str=None) -> dict:
        """
        Similar to `get_projects`, but retrieving all projects without pagination.

        **Documentation**:
            https://forge.autodesk.com/en/docs/data/v2/reference/http/hubs-hub_id-projects-GET

        Args:
            hub_id (str): ID of a hub to list the projects for.

        Returns:
            list(dict): List of projects parsed from the response JSON.

        Examples:
            ```
            THREE_LEGGED_TOKEN = os.environ["THREE_LEGGED_TOKEN"]
            client = DataManagementClient(SimpleTokenProvider(THREE_LEGGED_TOKEN))
            projects = client.get_all_projects("some-hub-id")
            print(projects)
            ```
        """
        headers = { "Content-Type": "application/vnd.api+json" }
        params = {}
        if filter_id:
            params["filter[id]"] = filter_id
        endpoint = "/hubs/{}/projects".format(hub_id)
        return self._get_paginated(endpoint, scopes=READ_SCOPES, headers=headers, params=params)
