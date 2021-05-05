import unittest
from .context import ModelDerivativeClient, urnify, OAuthTokenProvider, FORGE_CLIENT_ID, FORGE_CLIENT_SECRET, FORGE_BUCKET

class ModelDerivativeClientTestSuite(unittest.TestCase):
    """Forge Model Derivative client test cases."""

    def setUp(self):
        self.client = ModelDerivativeClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))

    def test_get_formats(self):
        formats = self.client.get_formats()
        assert formats

    def test_urnify(self):
        urn = urnify('test')
        assert urn == 'dGVzdA'

    # def test_get_thumbnail(self):
    #     png = self.client.get_thumbnail('dXJuOmFkc2sub2JqZWN0czpvcy5vYmplY3Q6cGV0cmJyb3otc2FtcGxlcy9ybWVfYmFzaWNfc2FtcGxlX3Byb2plY3QucnZ0')
    #     assert png
    #     with open("thumbnail.png", "wb") as output:
    #         output.write(png)

    # def test_get_manifest(self):
    #     manifest = self.client.get_manifest('dXJuOmFkc2sub2JqZWN0czpvcy5vYmplY3Q6cGV0cmJyb3otc2FtcGxlcy9ybWVfYmFzaWNfc2FtcGxlX3Byb2plY3QucnZ0')
    #     assert manifest

if __name__ == "__main__":
    unittest.main()