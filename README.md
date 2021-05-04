# autodesk-forge-sdk

Unofficial [Autodesk Forge](https://forge.autodesk.com) SDK for Python 3.* and above.

## Usage

```bash
pip3 install autodesk-forge-sdk
```

```python
import os
from autodesk_forge_sdk import AuthenticationClient

FORGE_CLIENT_ID = os.environ["FORGE_CLIENT_ID"]
FORGE_CLIENT_SECRET = os.environ["FORGE_CLIENT_SECRET"]

client = AuthenticationClient()
auth = client.authenticate(FORGE_CLIENT_ID, FORGE_CLIENT_SECRET, ["viewables:read"])
print(auth["access_token"])
```