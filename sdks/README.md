# Next-IOT SDKs

Generate clients from the live OpenAPI document:

```bash
export OPENAPI_URL=http://localhost:8000/openapi.json
./scripts/generate_sdks.sh
```

## Python (`next-iot-python-sdk`)

```bash
pip install -e sdks/python
```

```python
from next_iot_sdk import ApiClient, Configuration
from next_iot_sdk.api.sites_api import SitesApi

cfg = Configuration(host="http://localhost:8000", access_token="YOUR_TOKEN")
client = ApiClient(cfg)
sites = SitesApi(client).list_sites()
print(sites)
```

## TypeScript (`@next-iot/sdk`)

```bash
cd sdks/typescript && npm install && npm run build
```

```typescript
import { Configuration, SitesApi } from "@next-iot/sdk";

const api = new SitesApi(new Configuration({ basePath: "http://localhost:8000", accessToken: "YOUR_TOKEN" }));
const sites = await api.listSites();
console.log(sites);
```
