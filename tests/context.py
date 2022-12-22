import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from autodesk_forge_sdk import AuthenticationClient, Scope, get_authorization_url
from autodesk_forge_sdk import OAuthTokenProvider, SimpleTokenProvider
from autodesk_forge_sdk import OSSClient, DataManagementClient
from autodesk_forge_sdk import ModelDerivativeClient, urnify
from autodesk_forge_sdk import WebhooksClient
from autodesk_forge_sdk import AccountManagementClient, AccountManagementClient_BIM360
from autodesk_forge_sdk import DocumentManagementClient
from autodesk_forge_sdk import ReviewsClient
FORGE_CLIENT_ID = os.environ["FORGE_CLIENT_ID"]
FORGE_CLIENT_SECRET = os.environ["FORGE_CLIENT_SECRET"]
FORGE_BUCKET = os.environ["FORGE_BUCKET"]