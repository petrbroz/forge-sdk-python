from urllib.parse import quote
from .auth import BaseOAuthClient

BASE_URL = 'https://developer.api.autodesk.com/oss/v2'
READ_SCOPES = ['bucket:read', 'data:read']
WRITE_SCOPES = ['bucket:create', 'data:create', 'data:write']
DELETE_SCOPES = ['bucket:delete']

class OSSClient(BaseOAuthClient):
    def __init__(self, token_provider, base_url=BASE_URL):
        BaseOAuthClient.__init__(self, token_provider, base_url)

    def _get_paginated(self, url, scopes, params=None, headers=None):
        items = []
        while url:
            json = self._get(url, scopes, params, headers).json()
            items = items + json['items']
            if 'next' in json:
                url = json['next']
            else:
                url = None
        return items

    def get_buckets(self, region=None, limit=None, start_at=None):
        """Return the buckets owned by the application. This endpoint supports pagination.

        Parameters:
        region (string): Optional region where the bucket resides. Acceptable values: US, EMEA. Default: US.
        limit (int): Optional limit to the response size. Acceptable values: 1-100. Default = 10.
        start_at (string): Optional key to use as an offset to continue pagination This is typically the last bucket key found in a preceding 'GET buckets' response.

        Returns:
        object: Parsed response object with top-level properties 'items' and 'next'. See https://forge.autodesk.com/en/docs/data/v2/reference/http/buckets-GET/#body-structure-200 for more info.
        """
        params = {}
        if region:
            params['region'] = region
        if limit:
            params['limit'] = limit
        if start_at:
            params['startAt'] = start_at
        return self._get('/buckets', READ_SCOPES, params).json()

    def get_all_buckets(self, region=None):
        """Return all buckets owned by the application.

        Parameters:
        region (string): Optional region where the bucket resides. Acceptable values: US, EMEA. Default: US.

        Returns:
        list: List of objects representing individual buckets. See https://forge.autodesk.com/en/docs/data/v2/reference/http/buckets-GET/#body-structure-200 for more info.
        """
        params = {}
        if region:
            params['region'] = region
        return self._get_paginated('/buckets', READ_SCOPES, params)

    def get_bucket_details(self, bucket_key):
        """Return bucket details in JSON format if the caller is the owner of the bucket.
        A request by any other application will result in a response of 403 Forbidden.

        Returns:
        object: Parsed response object with bucket properties. See https://forge.autodesk.com/en/docs/data/v2/reference/http/buckets-:bucketKey-details-GET/#body-structure-200.
        """
        return self._get('/buckets/{}/details'.format(quote(bucket_key)), READ_SCOPES).json()

    def create_bucket(self, bucket_key, policy_key, region):
        """Creates a bucket. Buckets are arbitrary spaces that are created by applications
        and are used to store objects for later retrieval. A bucket is owned by the application
        that creates it.

        Parameters:
        bucket_key (string): A unique name you assign to a bucket. It must be globally unique across
            all applications and regions, otherwise the call will fail. Possible values: -_.a-z0-9
            (between 3-128 characters in length). Note that you cannot change a bucket key.
        policy_key (string): Data retention policy. Acceptable values: transient, temporary, persistent.
        region (string): The region where the bucket resides. Acceptable values: US, EMEA.
        """
        json = {
            'bucketKey': bucket_key,
            'policyKey': policy_key
        }
        headers = {
            'x-ads-region': region
        }
        return self._post('/buckets', WRITE_SCOPES, json=json, headers=headers).json()

    def delete_bucket(self, bucket_key):
        """Deletes a bucket. The bucket must be owned by the application.

        Parameters:
        bucket_key (string): Name of the bucket to be deleted.
        """
        return self._delete('/buckets/{}'.format(quote(bucket_key)), DELETE_SCOPES)

    def get_objects(self, bucket_key, limit=None, begins_with=None, start_at=None):
        """List objects in a bucket. It is only available to the bucket creator.

        Parameters:
        bucket_key (string): Bucket key for which to get details.
        limit (int): Optional number of objects to return in the result set. Acceptable values = 1 - 100. Default = 10.
        begins_with (string): Optional string to filter the result set by. The result set is restricted to items whose objectKey begins with the provided string.
        start_at (string): Optional position to start listing the result set.

        Returns:
        object: Parsed response object with top-level properties 'items' and 'next'. See https://forge.autodesk.com/en/docs/data/v2/reference/http/buckets-:bucketKey-objects-GET/#body-structure-200.
        """
        params = {}
        if limit:
            params['limit'] = limit
        if begins_with:
            params['beginsWith'] = begins_with
        if start_at:
            params['startAt'] = start_at
        return self._get('/buckets/{}/objects'.format(quote(bucket_key)), READ_SCOPES, params).json()

    def get_all_objects(self, bucket_key, begins_with=None):
        """Return all objects in bucket.

        Parameters:
        begins_with (string): Optional string to filter the result set by. The result set is restricted to items whose objectKey begins with the provided string.

        Returns:
        list: List of objects. See https://forge.autodesk.com/en/docs/data/v2/reference/http/buckets-:bucketKey-objects-GET/#body-structure-200.
        """
        params = {}
        if begins_with:
            params['beginsWith'] = begins_with
        return self._get_paginated('/buckets/{}/objects'.format(quote(bucket_key)), READ_SCOPES, params)

    def get_object_details(self, bucket_key, object_key):
        """Returns object details in JSON format.

        Parameters:
        bucket_key (string): Bucket key.
        object_key (string): Object name to get details for.

        Returns:
        object: Parsed response object with top-level properties 'items' and 'next'. See https://forge.autodesk.com/en/docs/data/v2/reference/http/buckets-:bucketKey-objects-:objectName-details-GET/#body-structure-200.
        """
        url = '/buckets/{}/objects/{}'.format(quote(bucket_key), quote(object_key))
        return self._get(url, READ_SCOPES).json()

    def upload_object(self, bucket_key, object_key, buff):
        """Upload an object. If the specified object name already exists in the bucket,
        the uploaded content will overwrite the existing content for the bucket name/object name combination.

        Parameters:
        bucket_key (string): Bucket key.
        object_key (string): Name of the object to be created.
        buff (file|buffer): Content to upload.

        Returns:
        object: Parsed response object with top-level properties 'items' and 'next'. See https://forge.autodesk.com/en/docs/data/v2/reference/http/buckets-:bucketKey-objects-:objectName-PUT/#body-structure-200.
        """
        url = '/buckets/{}/objects/{}'.format(quote(bucket_key), quote(object_key))
        return self._put(url, WRITE_SCOPES, buff=buff).json()

    def delete_object(self, bucket_key, object_key):
        """Deletes an object from the bucket.

        Parameters:
        bucket_key (string): Bucket key.
        object_key (string): Name of the object to be removed.
        """
        url = '/buckets/{}/objects/{}'.format(quote(bucket_key), quote(object_key))
        return self._delete(url, DELETE_SCOPES)