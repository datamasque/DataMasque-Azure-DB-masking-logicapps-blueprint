import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def _session() -> requests.Session:
    """A requests Session that retries transient token-endpoint failures.

    Unlike the ARM session in microsoft_sql, POST is retried here: the
    client-credentials grant is idempotent, so a retried request just issues
    another token.
    """
    retry = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("POST",),
        respect_retry_after_header=True,
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


class Token:
    """Client-credentials access token for Azure Resource Manager.

    Uses the v2.0 oauth2 token endpoint (scope-based). For production prefer a
    managed identity via azure-identity's DefaultAzureCredential instead of a
    client secret.
    """

    def __init__(self, tenant_id: str, client_id: str, secret: str) -> None:
        self.__tenant_id = tenant_id
        self.__client_id = client_id
        self.__secret = secret
        self.__session = _session()

    def get_access_token(self) -> str:
        token_url = f"https://login.microsoftonline.com/{self.__tenant_id}/oauth2/v2.0/token"
        body_data = {
            "client_id": self.__client_id,
            "client_secret": self.__secret,
            "grant_type": "client_credentials",
            "scope": "https://management.azure.com/.default",
        }
        res = self.__session.post(
            token_url,
            data=body_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        res.raise_for_status()
        return res.json()["access_token"]
