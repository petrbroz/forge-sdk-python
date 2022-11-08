import unittest
from .context import WebhooksClient, OAuthTokenProvider, FORGE_CLIENT_ID, FORGE_CLIENT_SECRET

class WebhooksTestSuite(unittest.TestCase):
    """Forge Data Management OSS client test cases."""

    def setUp(self):
        self.client = WebhooksClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))

    def test_get_webhooks(self):
        '''
        test that list of webhooks can retrieved.
        '''
        pages = self.client.get_webhooks()

        assert isinstance(pages, list)

        if len(pages) > 0:

            for page in pages:

                assert 'links' in page
                assert 'data' in page

                if len (page['data']):

                    assert 'hookId' in page['data']

if __name__ == "__main__":
    unittest.main()
