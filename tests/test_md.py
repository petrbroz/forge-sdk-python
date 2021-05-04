import unittest
from .context import ModelDerivativeClient, urnify, ActiveTokenProvider, FORGE_CLIENT_ID, FORGE_CLIENT_SECRET, FORGE_BUCKET

class ModelDerivativeClientTestSuite(unittest.TestCase):
    """Forge Model Derivative client test cases."""

    def setUp(self):
        self.client = ModelDerivativeClient(ActiveTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))

    def test_get_formats(self):
        formats = self.client.get_formats()
        assert formats

    def test_urnify(self):
        urn = urnify('test')
        assert urn == 'dGVzdA'

if __name__ == "__main__":
    unittest.main()