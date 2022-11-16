import unittest
from .context import OSSClient, DataManagementClient, DocumentManagementClient, OAuthTokenProvider, FORGE_CLIENT_ID, FORGE_CLIENT_SECRET, FORGE_BUCKET

class OSSClientTestSuite(unittest.TestCase):
    """Forge Data Management OSS client test cases."""

    def setUp(self):
        self.client = OSSClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))

    def test_get_buckets(self):
        page = self.client.get_buckets(limit=2)
        assert 'items' in page
        assert 'next' in page
        assert len(page['items']) <= 2

    def test_get_all_buckets(self):
        buckets = self.client.get_all_buckets()
        assert buckets

    def test_get_bucket_details(self):
        details = self.client.get_bucket_details(FORGE_BUCKET)
        assert 'bucketKey' in details

    def test_get_objects(self):
        page = self.client.get_objects(FORGE_BUCKET, limit=2)
        assert 'items' in page
        assert 'next' in page
        assert len(page['items']) <= 2

    def test_get_all_objects(self):
        objects = self.client.get_all_objects(FORGE_BUCKET)
        assert objects
    
    def test_upload_object_buff(self):
        buff = bytes('This is a test...', 'utf-8')
        obj = self.client.upload_object(FORGE_BUCKET, 'unittest.txt', buff)
        assert obj

    def test_upload_object_file(self):
        with open(__file__, 'rb') as file:
            obj = self.client.upload_object(FORGE_BUCKET, 'unittest.py', file)
            assert obj

    def test_get_object_details(self):
        details = self.client.get_object_details(FORGE_BUCKET, 'unittest.txt')
        assert 'objectKey' in details

class DataManagementTestSuite(unittest.TestCase):
    """Forge Data Management client test cases."""

    def setUp(self):
        self.data_client = DataManagementClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
        self.docm_client = DocumentManagementClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))

    def test_get_all_hubs(self):
        hubs = self.data_client.get_all_hubs()
        self.assertIsNotNone(hubs)

    def test_get_projects(self):

        hubs = self.data_client.get_all_hubs()
        self.assertIsNotNone(hubs)

        projects = self.data_client.get_projects(hubs[0]['id'])
        self.assertIsNotNone(projects)


    def test_get_folder_permissions(self):

        hubs = self.data_client.get_all_hubs()
        self.assertIsNotNone(hubs)

        projects = self.data_client.get_projects(hubs[0]['id'])
        self.assertIsNotNone(projects)

        project_id = projects['data'][0]['id'].split('b.')[1]

        root_folder_id = projects["data"][0]['relationships']["rootFolder"]["data"]["id"]

        projects = self.docm_client.get_folder_permissions(project_id, root_folder_id)
        self.assertIsNotNone(projects)

        if len(projects) > 0:

            project = projects[0]
            assert 'actions' in project


if __name__ == "__main__":
    unittest.main()
