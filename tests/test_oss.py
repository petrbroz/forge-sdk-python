import unittest
from .context import OSSClient, ActiveTokenProvider, FORGE_CLIENT_ID, FORGE_CLIENT_SECRET, FORGE_BUCKET

class OSSClientTestSuite(unittest.TestCase):
    """Forge Data Management OSS client test cases."""

    def setUp(self):
        self.client = OSSClient(ActiveTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))

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

if __name__ == "__main__":
    unittest.main()