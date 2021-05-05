from enum import Enum
from urllib.parse import quote
from .auth import BaseOAuthClient, Scope, TokenProviderInterface, SimpleTokenProvider, OAuthTokenProvider

BASE_URL = 'https://developer.api.autodesk.com/oss/v2'
READ_SCOPES = [Scope.BucketRead, Scope.DataRead]
WRITE_SCOPES = [Scope.BucketCreate, Scope.DataCreate, Scope.DataWrite]
DELETE_SCOPES = [Scope.BucketDelete]

class DataRetention(Enum):
    """
    Data retention policies.
    """
    Transient = 'transient'
    """
    Think of this type of storage as a cache. Use it for ephemeral results. For example, you might use this for objects
    that are part of producing other persistent artifacts, but otherwise are not required to be available later.

    Objects older than 24 hours are removed automatically. Each upload of an object is considered unique, so, for example,
    if the same rendering is uploaded multiple times, each of them will have its own retention period of 24 hours.
    """
    Temporary = 'temporary'
    """
    This type of storage is suitable for artifacts produced for user-uploaded content where after some period of activity,
    the user may rarely access the artifacts.

    When an object has reached 30 days of age, it is deleted.
    """
    Persistent = 'persistent'
    """
    Persistent storage is intended for user data. When a file is uploaded, the owner should expect this item
    to be available for as long as the owner account is active, or until he or she deletes the item.
    """

class OSSClient(BaseOAuthClient):
    """
    Forge Data Management object storage client.

    **Documentation**: https://forge.autodesk.com/en/docs/data/v2/reference/http
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

    def _get_paginated(self, url: str, scopes: list[Scope], params: dict=None, headers: dict=None) -> list:
        items = []
        while url:
            json = self._get(url, scopes, params, headers).json()
            items = items + json['items']
            if 'next' in json:
                url = json['next']
            else:
                url = None
        return items

    def get_buckets(self, region: str=None, limit: int=None, start_at: str=None) -> dict:
        """
        List buckets owned by the application, using pagination.

        **Documentation**: https://forge.autodesk.com/en/docs/data/v2/reference/http/buckets-GET

        Args:
            region (str, optional): Region where the bucket resides. Acceptable values: US, EMEA. Default: US.
            limit (int, optional): Limit to the response size. Acceptable values: 1-100. Default = 10.
            start_at (str, optional): Key to use as an offset to continue pagination. This is typically the last bucket key found in a preceding `get_buckets` response.

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
            params['region'] = region
        if limit:
            params['limit'] = limit
        if start_at:
            params['startAt'] = start_at
        return self._get('/buckets', READ_SCOPES, params).json()

    def get_all_buckets(self, region: str=None) -> list:
        """
        List all buckets owned by the application. Similar to `OSSClient.get_buckets` but returning all results without pagination.

        **Documentation**: https://forge.autodesk.com/en/docs/data/v2/reference/http/buckets-GET

        Args:
            region (str, optional): Region where the bucket resides. Acceptable values: US, EMEA. Default: US.

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
            params['region'] = region
        return self._get_paginated('/buckets', READ_SCOPES, params)

    def get_bucket_details(self, bucket_key: str) -> dict:
        """
        Get bucket details in JSON format if the caller is the owner of the bucket.
        A request by any other application will result in a response of 403 Forbidden.

        **Documentation**: https://forge.autodesk.com/en/docs/data/v2/reference/http/buckets-:bucketKey-details-GET

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
        return self._get('/buckets/{}/details'.format(quote(bucket_key)), READ_SCOPES).json()

    def create_bucket(self, bucket_key: str, data_retention_policy: DataRetention, region: str) -> dict:
        """
        Create a bucket. Buckets are arbitrary spaces that are created by applications
        and are used to store objects for later retrieval. A bucket is owned by the application
        that creates it.

        **Documentation**: https://forge.autodesk.com/en/docs/data/v2/reference/http/buckets-POST

        Args:
            bucket_key (str): A unique name you assign to a bucket. It must be globally unique across
                all applications and regions, otherwise the call will fail. Possible values: -_.a-z0-9
                (between 3-128 characters in length). Note that you cannot change a bucket key.
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
            details = client.create_bucket(FORGE_BUCKET, DataRetention.Temporary, "US")
            print(details)
            ```
        """
        json = {
            'bucketKey': bucket_key,
            'policyKey': data_retention_policy.value
        }
        headers = {
            'x-ads-region': region
        }
        return self._post('/buckets', WRITE_SCOPES, json=json, headers=headers).json()

    def delete_bucket(self, bucket_key: str):
        """
        Delete a bucket. The bucket must be owned by the application.

        **Documentation**: https://forge.autodesk.com/en/docs/data/v2/reference/http/buckets-:bucketKey-DELETE

        Args:
            bucket_key (str): Name of the bucket to be deleted.
        """
        self._delete('/buckets/{}'.format(quote(bucket_key)), DELETE_SCOPES)

    def get_objects(self, bucket_key: str, limit: int=None, begins_with: str=None, start_at: str=None) -> dict:
        """
        List objects in bucket, using pagination. It is only available to the bucket creator.

        **Documentation**: https://forge.autodesk.com/en/docs/data/v2/reference/http/buckets-:bucketKey-objects-GET

        Args:
            bucket_key (str): Bucket key for which to get details.
            limit (int, optional): Number of objects to return in the result set. Acceptable values = 1 - 100. Default = 10.
            begins_with (str, optional): String to filter the result set by. The result set is restricted to items whose objectKey begins with the provided string.
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
        if limit:
            params['limit'] = limit
        if begins_with:
            params['beginsWith'] = begins_with
        if start_at:
            params['startAt'] = start_at
        return self._get('/buckets/{}/objects'.format(quote(bucket_key)), READ_SCOPES, params).json()

    def get_all_objects(self, bucket_key: str, begins_with: str=None) -> list:
        """
        List all objects in bucket. Similar to `OSSClient.get_objects` but returning all results without pagination.

        Args:
            begins_with (str, optional): String to filter the result set by. The result set is restricted to items whose objectKey begins with the provided string.

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
            params['beginsWith'] = begins_with
        return self._get_paginated('/buckets/{}/objects'.format(quote(bucket_key)), READ_SCOPES, params)

    def get_object_details(self, bucket_key: str, object_key: str) -> dict:
        """
        Get object details in JSON format.

        **Documentation**: https://forge.autodesk.com/en/docs/data/v2/reference/http/buckets-:bucketKey-objects-:objectName-details-GET

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
        url = '/buckets/{}/objects/{}'.format(quote(bucket_key), quote(object_key))
        return self._get(url, READ_SCOPES).json()

    def upload_object(self, bucket_key: str, object_key: str, buff) -> list:
        """
        Upload an object. If the specified object name already exists in the bucket,
        the uploaded content will overwrite the existing content for the bucket name/object name combination.

        **Documentation**: https://forge.autodesk.com/en/docs/data/v2/reference/http/buckets-:bucketKey-objects-:objectName-PUT

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
        url = '/buckets/{}/objects/{}'.format(quote(bucket_key), quote(object_key))
        return self._put(url, WRITE_SCOPES, buff=buff).json()

    def delete_object(self, bucket_key: str, object_key: str):
        """
        Delete an object from bucket.

        **Documentation**: https://forge.autodesk.com/en/docs/data/v2/reference/http/buckets-:bucketKey-objects-:objectName-DELETE

        Args:
            bucket_key (str): Bucket key.
            object_key (str): Name of the object to be removed.
        """
        url = '/buckets/{}/objects/{}'.format(quote(bucket_key), quote(object_key))
        self._delete(url, DELETE_SCOPES)