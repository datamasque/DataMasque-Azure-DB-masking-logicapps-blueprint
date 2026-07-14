"""Service-principal credential resolution for the Azure Functions.

Credentials are provisioned as Function App settings (TENANT_ID, CLIENT_ID,
CLIENT_SECRET). Functions read them from the environment rather than passing
the client secret between steps in plaintext HTTP response bodies.
"""
import os
from typing import Tuple


def service_principal(req_body: dict) -> Tuple[str, str, str]:
    """Return (tenant_id, client_id, client_secret).

    Prefers the Function App settings; falls back to the request body only for
    fields not configured in the environment (backward compatibility).
    """
    tenant_id = os.environ.get("TENANT_ID") or req_body.get("TenantID")
    client_id = os.environ.get("CLIENT_ID") or req_body.get("ClientID")
    client_secret = os.environ.get("CLIENT_SECRET") or req_body.get("ClientSecret")
    return tenant_id, client_id, client_secret
