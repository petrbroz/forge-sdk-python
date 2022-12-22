import unittest

from .context import (FORGE_CLIENT_ID, FORGE_CLIENT_SECRET,
                      RelationshipManagementClient,
                      DataManagementClient, OAuthTokenProvider)


class RelationshipsTestSuite(unittest.TestCase):
    """Forge Relationship client test cases."""

    def setUp(self):
        self.relationship_client = RelationshipManagementClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
        self.datam_client = DataManagementClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))

    def test_get_relationships(self):
        '''
        test get_relationships. returns all relationships from project contianer.
        '''

        hubs = self.datam_client.get_all_hubs()

        self.assertIsNotNone(hubs)

        assert len(hubs) > 0, "No hubs found"

        projects = self.datam_client.get_projects(hubs[0]['id'])
        self.assertIsNotNone(projects)

        assert 'data' in projects
        self.assertIsInstance(projects['data'], list)
        project = projects['data'][0]

        assert len(project) > 0, "no data in project"
        assert 'id' in project, "No project ID in project object"
        
        container_id = projects['data'][12]['relationships']['issues']['data']['id']

        relationships = self.relationship_client.get_relationships(container_id)

if __name__ == "__main__":
    unittest.main()