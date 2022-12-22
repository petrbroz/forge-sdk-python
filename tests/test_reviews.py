import os
import unittest
from .context import DataManagementClient, ReviewsClient, SimpleTokenProvider, OAuthTokenProvider, FORGE_CLIENT_ID, FORGE_CLIENT_SECRET

class ReviewsTestSuite(unittest.TestCase):
    """Reviews client test cases."""

    def setUp(self):
        THREE_LEGGED_TOKEN = os.environ["THREE_LEGGED_TOKEN"]

        self.data_client = DataManagementClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
        self.client = ReviewsClient(SimpleTokenProvider({"access_token": THREE_LEGGED_TOKEN}))

        hubs = self.data_client.get_all_hubs()
        self.assertIsNotNone(hubs)

        projects = self.data_client.get_projects(hubs[0]['id'])
        self.project_id = projects['data'][0]['id'].split('b.')[1]
        self.review_id = None

    def test_a_get_reviews(self):
        '''
        test that list of reviews can be retrieved.
        '''
        pages = self.client.get_reviews(self.project_id)
        
        assert isinstance(pages, list)

        self.review_id = pages[0]["id"]
    
    def test_b_get_review(self):

        pages = self.client.get_review(self.project_id, self.review_id)
        self.assertIn('results', pages)
        self.assertNotIsInstance(pages["results"], list)

if __name__ == "__main__":
    unittest.main()
