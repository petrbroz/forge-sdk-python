import unittest
from .context import DataManagementClient, DocumentManagementClient, Action, Subject, OAuthTokenProvider, FORGE_CLIENT_ID, FORGE_CLIENT_SECRET


class DocumentManagementTestSuite(unittest.TestCase):
    """Forge Data Management client test cases."""

    def setUp(self):
        self.data_client = DataManagementClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))
        self.docm_client = DocumentManagementClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))

    def test_get_folder_permissions(self):

        hubs = self.data_client.get_all_hubs()
        self.assertIsNotNone(hubs)

        projects = self.data_client.get_projects(hubs[0]['id'])
        self.assertIsNotNone(projects)

        project_id = projects['data'][0]['id'].split('b.')[1]

        root_folder_id = projects["data"][0]['relationships']["rootFolder"]["data"]["id"]

        users = self.docm_client.get_folder_permissions(project_id, root_folder_id)
        self.assertIsNotNone(projects)

        if len(users) > 0:

            user = users[0]
            assert 'actions' in user

    def test_batch_update_permissions(self):

        hubs = self.data_client.get_all_hubs()
        self.assertIsNotNone(hubs)

        projects = self.data_client.get_projects(hubs[0]['id'])
        self.assertIsNotNone(projects)

        project_id = projects['data'][0]['id'].split('b.')[1]

        folder_id = projects["data"][0]['relationships']["rootFolder"]["data"]["id"]

        users = self.docm_client.get_folder_permissions(project_id, folder_id)
        self.assertIsNotNone(projects)

        if len(users) > 0:

            user = users[0]
            assert 'actions' in user

            actions = user['actions']

            subject = Subject(user['subjectId'], user['subjectType'], Action.VIEW_OLNY)
            
            # Action.VIEW_OLNY
            response = self.docm_client.batch_update_permissions(project_id, folder_id, [subject])

            # roll back actions as before update
            subject = Subject(user['subjectId'], user['subjectType'], actions)
            response = self.docm_client.batch_update_permissions(project_id, folder_id, [subject])
