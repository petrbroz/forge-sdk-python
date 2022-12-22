"""
Clients for working with the Forge Document Management service.
"""
# from os import path
from enum import Enum
from typing import Dict, List, Union
from urllib import request, parse
from .auth import BaseOAuthClient, Scope, TokenProviderInterface

BASE_URL = "https://developer.api.autodesk.com"
DOCUMENT_MANAGEMENT_URL = f"{BASE_URL}/bim360/docs/v1"
READ_SCOPES = [Scope.BUCKET_READ, Scope.DATA_READ]
WRITE_SCOPES = [Scope.BUCKET_CREATE, Scope.DATA_CREATE, Scope.DATA_WRITE]
DELETE_SCOPES = [Scope.BUCKET_DELETE]

class Action(Enum):
    """
    The six permission levels in BIM 360 Document Management correspond to one or more actions

    Example: Action.VIEW_ONLY corresponds to the actions ["VIEW", "COLLABORATE"].

    **Documentation**: https://forge.autodesk.com/en/docs/acc/v1/reference/http/document-management-projects-project_id-folders-folder_id-permissionsbatch-update-POST/#body-structure 
    """
    VIEW_OLNY = ["VIEW", "COLLABORATE"]
    VIEW_DOWNLOAD = VIEW_OLNY + ["DOWNLOAD"]
    UPLOAD_ONLY = ["PUBLISH"]
    VIEW_DOWNLOAD_UPLOAD = VIEW_DOWNLOAD + UPLOAD_ONLY
    VIEW_DOWNLOAD_UPLOAD_EDIT = VIEW_DOWNLOAD_UPLOAD + ["EDIT"]
    FULL_CONTROLLER = VIEW_DOWNLOAD_UPLOAD_EDIT + ["CONTROL"]

class Subject:

    def __init__(self, subject_id: str, subject_type: str, actions: Union[Action, list]):

        if isinstance(actions, Action):
            actions = actions.value

        self.subject_id = subject_id
        self.subject_type = subject_type
        self.actions = actions

    def to_dict(self):

        return {
            "subjectId":self.subject_id,
            "subjectType":self.subject_type,
            "actions":self.actions
        }

class DocumentManagementClient(BaseOAuthClient):
    """
    Forge Document Management client.

    **Documentation**: https://forge.autodesk.com/en/docs/data/v2/reference/http
    """

    def __init__(
        self, token_provider: TokenProviderInterface):
        """
        Create new instance of the client.

        Args:
            token_provider (autodesk_forge_sdk.auth.TokenProviderInterface):
                Provider that will be used to generate access tokens for API calls.

                Use `autodesk_forge_sdk.auth.OAuthTokenProvider` if you have your app's client ID
                and client secret available, `autodesk_forge_sdk.auth.SimpleTokenProvider`
                if you would like to use an existing access token instead, or even your own
                implementation of the `autodesk_forge_sdk.auth.TokenProviderInterface` interface.

                Note that many APIs in the Forge Data Management service require
                a three-legged OAuth token.
            base_url (str, optional): Base URL for API calls.

        Examples:
            ```
            THREE_LEGGED_TOKEN = os.environ["THREE_LEGGED_TOKEN"]
            client = DataManagementClient(SimpleTokenProvider(THREE_LEGGED_TOKEN))
            ```
        """
        BaseOAuthClient.__init__(self, token_provider, DOCUMENT_MANAGEMENT_URL)

    def _get_paginated(self, url: str, **kwargs) -> List:
        items = []
        while url:
            json = self._get(url, **kwargs).json()
            items = items + json["items"]
            if "next" in json:
                url = json["next"]
            else:
                url = None
        return items

    
    def get_naming_standard(self, project_id: str, naming_standard_ids: Union[str, dict]) -> Dict:
        """
        Retrieves the file naming standard for a project..

        **Documentation**: https://forge.autodesk.com/en/docs/acc/v1/reference/http/document-management-naming-standards-id-GET/

        Args:
            project_id (str, required): project ID
            naming_standard_id (str, required): naming standard ID.

        Returns:
            list(dict): List of hubs parsed from the response JSON.

        Examples:
            ```
            THREE_LEGGED_TOKEN = os.environ["THREE_LEGGED_TOKEN"]
            client = DocumentManagementClient(SimpleTokenProvider(THREE_LEGGED_TOKEN))
            naming_standard = client.get_naming_standard(project_id, naming_standard_id)
            print(naming_standard)
            ```
        """

        if isinstance(naming_standard_ids, dict):

            naming_standard_ids: list = naming_standard_ids['attributes']['extension']['data']['namingStandardIds']
        
        else:

            naming_standard_ids: list = [naming_standard_ids]

        # check if more than one naming standard is applied to folder.
        assert len(naming_standard_ids) > 0, f"No namingStandard in list '{naming_standard_ids}'"

        assert len(naming_standard_ids) <= 1, (
            'Assuming only one "file naming standard" '
            'per folder. Has ACC changed to support more than one? see: '
            'https://forge.autodesk.com/en/docs/acc/v1/reference/http/document-management-naming-standards-id-GET/. '
            f"INFO: {len(naming_standard_ids)} namings standard ids returned "
            )


        headers = { "Content-Type": "application/vnd.api+json" }

        return self._get(f"/projects/{project_id}/naming-standards/{naming_standard_ids[0]}",
            scopes=READ_SCOPES, headers=headers).json()
    
    def get_custom_attribute_definitions_for_docs(self, project_id: str, urns: list) -> Dict:
        """
        Retrieves a list of custom attribute values for multiple Document Management documents..

        **Documentation**:
        https://forge.autodesk.com/en/docs/bim360/v1/reference/http/document-management-versionsbatch-get-POST/

        Args:
            project_id (str, required): project ID
            urns (list, required): A list of version IDs or item IDs. If you use item IDs it retrieves the values for the latest (tip) versions. You can specify up to 50 documents.

        Returns:
            Dict: dictionary containing custom attribute.

        """
        headers = { "Content-Type": "application/vnd.api+json" }
        data = {"urns": urns}

        return self._post(f"{DOCUMENT_MANAGEMENT_URL}/projects/{project_id}/versions:batch-get",
        scopes=READ_SCOPES, headers=headers, json=data).json()
    
    def get_custom_attribute_definitions(self, project_id, folder_id) -> Dict:
        """
        Retrieves a complete list of custom attribute definitions for all the documents
        in a specific folder, including custom attributes that have not been assigned a
        value, as well as the potential drop-down (array) values.

        **Documentation**:
        https://forge.autodesk.com/en/docs/acc/v1/reference/http/document-management-custom-attribute-definitions-GET/

        Args:
            project_id (str, required): project ID
            folder_id (str, required): Folder ID where where namingstandard applies.

        Returns:
            Dict: dictoionary of naming standard from the JSON response.

        """
        headers = { "Content-Type": "application/vnd.api+json" }

        return self._get(f"{DOCUMENT_MANAGEMENT_URL}/projects/{project_id}/folders/{folder_id}/custom-attribute-definitions",
        scopes=READ_SCOPES, headers=headers).json()
    
    def batch_update_custom_attribute_definitions(self, project_id, version_id, attributes: dict) -> Dict:
        """
        Assigns values to custom attributes for multiple documents. This endpoint also clears custom attribute values.

        **Documentation**:
        https://forge.autodesk.com/en/docs/acc/v1/reference/http/document-management-custom-attributesbatch-update-POST

        Args:
            project_id (str): project ID
            version_id (str): The URL-encoded ID (URN) of the version.
            new_values (dict): new values for custom attributes. ex: [{"id": 1001,"value": "checked"},{"id": 1002,"value": "2020-03-31T16:00:00.000Z"}]

        Returns:
            Dict: dictionary of assigned values for the custom attributes .

        """
        version_id = parse.quote(version_id)

        headers = { "Content-Type": "application/vnd.api+json" }

        return self._post(f"{DOCUMENT_MANAGEMENT_URL}/projects/{project_id}/versions/{version_id}/custom-attributes:batch-update",
        scopes=READ_SCOPES, headers=headers, json=attributes).json()
    
    def get_folder_permissions(self, project_id, folder_id) -> Dict:
        """
        Retrieves information about the permissions assigned to users, roles and companies for a BIM 360 Document Management folder,
        including details about the name and the status.

        **Documentation**:
        https://forge.autodesk.com/en/docs/acc/v1/reference/http/document-management-projects-project_id-folders-folder_id-permissions-GET/

        Args:
            project_id (str, required): The ID of the project. This corresponds to project ID in the Data Management API. To convert a project ID in the Data Management API into a project ID in the BIM 360 API you need to remove the “b.” prefix.
            folder_id (str, required): The ID (URN) of the folder.

        Returns:
            Dict: a list of dictionaries containing data on the users with access and their permissions

        """
        headers = { "Content-Type": "application/json" }

        return self._get(f"{DOCUMENT_MANAGEMENT_URL}/projects/{project_id}/folders/{folder_id}/permissions",
        scopes=READ_SCOPES, headers=headers).json()
    
    def batch_update_permissions(self, project_id: str, folder_id: str, subject: Union[List[Subject], List[dict]]) -> Dict:
        """
        Updates the permissions assigned to multiple users, roles, and companies for a folder. This endpoint replaces the permissions that were previously assigned to the user for this folder.

        **Documentation**:
        https://forge.autodesk.com/en/docs/acc/v1/reference/http/document-management-projects-project_id-folders-folder_id-permissionsbatch-update-POST/

        Args:
            project_id (str, required): The ID of the project. This corresponds to project ID in the Data Management API. To convert a project ID in the Data Management API into a project ID in the BIM 360 API you need to remove the “b.” prefix.
            
            folder_id (str, required): The ID (URN) of the folder.

            subject_id (str, required): The ID of the user, role, or company. To verify the subjectId of the user, role, or company, use GET permissions.

            subject (list[Subject] | list[dict], required): A list of subjects and permissions. Can be user, role, company. Example: [{'subjectId': '25339726-867a-49f1-9ba4-d48f353ab562', 'subjectType': 'USER', 'actions': ['VIEW', 'COLLABORATE']}] Where:
            autodesk_id (str, required): The Autodesk ID of the user, role or company.
            subject_type (str, required): The type of subject. Possible values: USER, COMPANY, ROLE.
            actions (list, required):Permitted actions for the user, role, or company. Possible values: PUBLISH, VIEW, DOWNLOAD, COLLABORATE, EDIT, CONTROL, PUBLISH_MARKUP.

        Returns:
            Dict: a list of dictionaries containing data on the users with access and their permissions

        """
        headers = { "Content-Type": "application/json" }

        for i, s in enumerate(subject):
            if isinstance(s, Subject):
                subject[i] = s.to_dict()

        return self._post(f"/projects/{project_id}/folders/{folder_id}/permissions:batch-update",
        scopes=WRITE_SCOPES, headers=headers, json=subject).json()