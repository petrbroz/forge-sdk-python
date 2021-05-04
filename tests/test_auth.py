import unittest
from .context import AuthenticationClient, FORGE_CLIENT_ID, FORGE_CLIENT_SECRET

class AuthenticationClientTestSuite(unittest.TestCase):
    """Forge Authentication client test cases."""

    def setUp(self):
        self.client = AuthenticationClient()

    def test_authenticate(self):
        token = self.client.authenticate(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET, ["viewables:read"])
        assert token["access_token"]

    def test_authorization_url(self):
        url = self.client.get_authorization_url(FORGE_CLIENT_ID, 'code', 'http://foo.bar', ["viewables:read"], 'randomstate')
        assert url

if __name__ == "__main__":
    unittest.main()