import base64
from urllib.parse import quote
from .auth import BaseOAuthClient

BASE_URL = 'https://developer.api.autodesk.com/modelderivative/v2'
WRITE_SCOPES = ['data:create', 'data:write', 'data:read']

def urnify(str):
    """Converts input string into base64-encoded string (without padding '=' characters)
    that can be used as Model Derivative service URN.
    """
    base64_bytes = base64.b64encode(str.encode('ascii'))
    ascii_output = base64_bytes.decode('ascii')
    return ascii_output.rstrip('=')

class ModelDerivativeClient(BaseOAuthClient):
    def __init__(self, token_provider, base_url=BASE_URL):
        BaseOAuthClient.__init__(self, token_provider, base_url)

    def get_formats(self):
        """Returns an up-to-date list of Forge-supported translations, that you can use to identify
        which types of derivatives are supported for each source file type.

        Returns:
        object: Parsed response object. For more information, see https://forge.autodesk.com/en/docs/model-derivative/v2/reference/http/formats-GET/#body-structure-200.
        """
        return self._get('/designdata/formats', []).json()

    def submit_job(self, urn, output_formats, output_region, root_filename=None, workflow_id=None, workflow_attr=None, force=False):
        """Translate a design from one format to another format.

        Parameters:
        urn (string): Base64-encoded ID of the object to translate.
        output_formats (list): List of objects representing all the requested outputs. Each object should have at least 'type' property set to 'svf', 'svf2', etc.
        output_region (string): Output region. Allowed values: 'US', 'EMEA'.
        root_filename (string): Optional starting filename if the converted file is a ZIP archive.
        workflow_id (string): Optional workflow ID.
        workflow_attr (object): Optional workflow payload.

        Returns:
        object: Parsed response object. For more information, see https://forge.autodesk.com/en/docs/model-derivative/v2/reference/http/job-POST/#body-structure-200-201.
        """
        json = {
            'input': {
                'urn': urn
            },
            'output': {
                'formats': output_formats,
                'destination': {
                    'region': output_region
                }
            }
        }
        if root_filename:
            json['input']['compressedUrn'] = True
            json['input']['rootFilename'] = root_filename
        if workflow_id:
            json['misc'] = { 'workflowId': workflow_id }
            if workflow_attr:
                json['misc']['workflowAttribute'] = workflow_attr
        headers = {}
        if force:
            headers['x-ads-force'] = 'true'
        # TODO: what about the EMEA endpoint?
        return self._post('/designdata/job', WRITE_SCOPES, json=json, headers=headers).json()