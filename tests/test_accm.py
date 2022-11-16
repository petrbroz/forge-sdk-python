import unittest

from .context import (FORGE_CLIENT_ID, FORGE_CLIENT_SECRET,
                      AccountManagementClient, AccountManagementClient_BIM360,
                      DataManagementClient, OAuthTokenProvider)


class WebhooksTestSuite(unittest.TestCase):
    """Forge Data Management OSS client test cases."""

    def setUp(self):
        self.accm_client = AccountManagementClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
        self.accm_client_bim360 = AccountManagementClient_BIM360(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
        self.datam_client = DataManagementClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))

    def test_get_project_users(self):
        '''
        test get_project_users. returns all users in a project.
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
        
        project_id = project['id']
        users = self.accm_client_bim360.get_project_users(project_id)

        assert isinstance(users, list)

        if len(users) > 0:

            user = users[0]

            assert 'services' in user

            assert isinstance(user['services'], list)

    def test_get_companies(self):
        '''
        test get_project_users. returns all users in a project.
        '''

        hubs = self.datam_client.get_all_hubs()
        self.assertIsNotNone(hubs)
        assert len(hubs) > 0, "No hubs found"

        account_id = hubs[0]['id'].split('b.')[1]
        companies = self.accm_client.get_companies(account_id)

        self.assertIsNotNone(hubs)



        assert len(hubs) > 0, "No hubs found"

        projects = self.datam_client.get_projects(hubs[0]['id'])
        self.assertIsNotNone(projects)
    
    def test_get_industry_roles(self):
        '''
        test get_project_users. returns all industry_roles in a project.
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
        
        project_id = project['id'].split('b.')[1]
        account_id = hubs[0]['id'].split('b.')[1]

        industry_roles = self.accm_client.get_industry_roles(account_id, project_id)

        assert isinstance(industry_roles, list)

        if len(industry_roles) > 0:

            industry_role = industry_roles[0]

            assert 'member_group_id' in industry_role

if __name__ == "__main__":
    unittest.main()