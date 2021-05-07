"""
View definitions.
"""

import os
from django.shortcuts import render
from autodesk_forge_sdk import AuthenticationClient, OSSClient, OAuthTokenProvider, urnify, Scope

FORGE_CLIENT_ID = os.environ["FORGE_CLIENT_ID"]
FORGE_CLIENT_SECRET = os.environ["FORGE_CLIENT_SECRET"]
FORGE_BUCKET = os.environ["FORGE_BUCKET"]
auth_client = AuthenticationClient()
oss_client = OSSClient(OAuthTokenProvider(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET))


def index(request):
    auth = auth_client.authenticate(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET, [Scope.VIEWABLES_READ])
    objects = map(
        lambda o: { 'name': o['objectKey'], 'urn': urnify(o['objectId']) },
        oss_client.get_all_objects(FORGE_BUCKET))
    context = {
        'objects': objects,
        'access_token': auth['access_token']
    }
    return render(request, 'index.html', context)
