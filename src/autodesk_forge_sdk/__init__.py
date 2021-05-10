"""
Clients for communicating with different Autodesk Forge services.
"""

from .auth import AuthenticationClient, Scope, get_authorization_url
from .auth import TokenProviderInterface, SimpleTokenProvider, OAuthTokenProvider
from .dm import OSSClient, DataManagementClient
from .md import ModelDerivativeClient, urnify
