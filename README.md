# autodesk-forge-sdk

Unofficial [Autodesk Forge](https://forge.autodesk.com) SDK for Python (3.*).

## Usage

Install the package from PyPI:

```bash
pip3 install autodesk-forge-sdk
```

### Authentication

```python
import os
from autodesk_forge_sdk import AuthenticationClient

client = AuthenticationClient()
auth = client.authenticate(os.environ["FORGE_CLIENT_ID"], os.environ["FORGE_CLIENT_SECRET"], ["viewables:read"])
print(auth["access_token"])
```

### Data Management

```python
import os
from autodesk_forge_sdk import OSSClient, ActiveTokenProvider

client = OSSClient(ActiveTokenProvider(os.environ["FORGE_CLIENT_ID"], os.environ["FORGE_CLIENT_SECRET"]))
buckets = client.get_all_buckets()
print(buckets)
```

Or, if you already have an access token:

```python
import os
from autodesk_forge_sdk import OSSClient, PassiveTokenProvider

client = OSSClient(PassiveTokenProvider(os.environ["FORGE_ACCESS_TOKEN"]))
buckets = client.get_all_buckets()
print(buckets)
```
