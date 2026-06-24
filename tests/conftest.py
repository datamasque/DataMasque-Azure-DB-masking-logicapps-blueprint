"""Test scaffolding for the Azure Functions.

The function packages use relative imports (`from ..services ...`) and read env
vars / import `azure.functions` at module load. We register the repo's
`functions/` directory as an importable package and stub the heavy Azure SDK
modules (plus `requests`/`urllib3`, which the provider/token modules import at
load time) so the pure logic can be unit-tested with only pytest installed — no
Azure environment and no third-party HTTP libraries required.
"""
import os
import sys
import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FUNCTIONS_DIR = REPO_ROOT / "functions"


def _stub_module(name, **attrs):
    mod = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(mod, key, value)
    sys.modules[name] = mod
    return mod


# --- Stub Azure SDK modules the functions import at load time ---
class _HttpRequest:  # minimal stand-in
    def __init__(self, body=None):
        self._body = body or {}

    def get_json(self):
        return self._body


class _HttpResponse:
    def __init__(self, body, mimetype=None, status_code=200):
        self.body = body
        self.status_code = status_code


_stub_module("azure")
_stub_module("azure.functions", HttpRequest=_HttpRequest, HttpResponse=_HttpResponse)
_stub_module("azure.keyvault")
_stub_module("azure.keyvault.secrets", SecretClient=object)
_stub_module("azure.identity", DefaultAzureCredential=object)

# --- Stub requests/urllib3 (pulled in transitively by microsoft_sql/token at
# import time). The unit-tested logic never makes a real HTTP call, so only the
# names imported at module load need to resolve. ---
_stub_module("requests", Session=object, get=None, post=None, put=None, delete=None)
_stub_module("requests.adapters", HTTPAdapter=object)
_stub_module("urllib3")
_stub_module("urllib3.util")
_stub_module("urllib3.util.retry", Retry=object)

# --- Default env the function modules read at import ---
os.environ.setdefault("SUBSCRIPTION_ID", "sub-test")
os.environ.setdefault("RESOURCE_GROUP", "rg-test")
os.environ.setdefault("TENANT_ID", "tenant-test")
os.environ.setdefault("CLIENT_ID", "client-test")
os.environ.setdefault("CLIENT_SECRET", "secret-test")
os.environ.setdefault("DATABASE_ID", "db-id-target")
os.environ.setdefault("DATAMASQUE_BASE_URL", "https://masque.test/")
os.environ.setdefault("DATAMASQUE_KEYVAULT", "https://kv.test/")
os.environ.setdefault("SECRET_NAME", "dm-secret")

# --- Register `functions/` as a package so relative imports resolve ---
if "functions" not in sys.modules:
    pkg = types.ModuleType("functions")
    pkg.__path__ = [str(FUNCTIONS_DIR)]
    sys.modules["functions"] = pkg
