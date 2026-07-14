import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..token import Token


def _session() -> requests.Session:
    """A requests Session that retries transient ARM throttling/5xx errors.

    Azure Resource Manager returns 429 with a Retry-After header when throttled;
    retrying with backoff avoids failing the workflow (and orphaning the staging
    server) on a transient throttle.

    POST is intentionally excluded: the only POST through this session is the
    database export, which is not idempotent — a retried transient 5xx could
    kick off a second export. GET/PUT/DELETE against ARM are safe to retry.
    """
    retry = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "PUT", "DELETE"),
        respect_retry_after_header=True,
    )
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    return session


class MicrosoftSQL:
    PROVIDES = "Microsoft.Sql"
    API_VERSION = "2021-11-01-preview"

    def __init__(self, tenant_id: str, client_id: str, secret: str, resource_group: str):
        self.__token = Token(tenant_id=tenant_id, client_id=client_id, secret=secret)
        self.__resource_group = resource_group
        self.__session = _session()

    def __auth_header(self, content_type: bool = False) -> dict:
        headers = {"Authorization": f"Bearer {self.__token.get_access_token()}"}
        if content_type:
            headers["Content-Type"] = "application/json"
        return headers

    def get_status_process(self, azure_async_operation: str):
        """Gets the status of a long-running operation in Azure."""
        return self.__session.get(url=azure_async_operation, headers=self.__auth_header())

    def get_configuration_sql_server(self, subscription_id: str, resource_group_name: str, server_name: str):
        """Get the configuration of a SQL server."""
        url = (
            "https://management.azure.com/subscriptions/{0}/resourceGroups/{1}"
            "/providers/{2}/servers/{3}?api-version={4}"
        ).format(subscription_id, resource_group_name, self.PROVIDES, server_name, self.API_VERSION)
        return self.__session.get(url, headers=self.__auth_header())

    def get_list_of_databases_from_server(self, subscription_id: str, resource_group_name: str, server_name: str):
        """Gets a list of databases on a server."""
        url = (
            "https://management.azure.com/subscriptions/{0}/resourceGroups/{1}"
            "/providers/{2}/servers/{3}/databases?api-version={4}"
        ).format(subscription_id, resource_group_name, self.PROVIDES, server_name, self.API_VERSION)
        return self.__session.get(url, headers=self.__auth_header())

    def creates_or_updates_server(self, subscription_id: str, server_name: str, body):
        """Creates or updates a server."""
        url = (
            "https://management.azure.com/subscriptions/{0}/resourceGroups/{1}"
            "/providers/{2}/servers/{3}?api-version={4}"
        ).format(subscription_id, self.__resource_group, self.PROVIDES, server_name, self.API_VERSION)
        return self.__session.put(url, headers=self.__auth_header(content_type=True), json=body)

    def create_or_update_database(self, subscription_id: str, server_name: str, database_name: str, body):
        """Creates a new database or updates an existing database."""
        url = (
            "https://management.azure.com/subscriptions/{0}/resourceGroups/{1}"
            "/providers/{2}/servers/{3}/databases/{4}?api-version={5}"
        ).format(subscription_id, self.__resource_group, self.PROVIDES, server_name, database_name, self.API_VERSION)
        return self.__session.put(url, headers=self.__auth_header(content_type=True), json=body)

    def export_database_to_blod_storage(self, subscription_id: str, server_name: str, database_name: str, body):
        """Exports a database to blob storage."""
        url = (
            "https://management.azure.com/subscriptions/{0}/resourceGroups/{1}"
            "/providers/{2}/servers/{3}/databases/{4}/export?api-version={5}"
        ).format(subscription_id, self.__resource_group, self.PROVIDES, server_name, database_name, self.API_VERSION)
        return self.__session.post(url, headers=self.__auth_header(content_type=True), json=body)

    def delete_server(self, subscription_id: str, server_name: str):
        """Deletes a server."""
        url = (
            "https://management.azure.com/subscriptions/{0}/resourceGroups/{1}"
            "/providers/{2}/servers/{3}?api-version={4}"
        ).format(subscription_id, self.__resource_group, self.PROVIDES, server_name, self.API_VERSION)
        return self.__session.delete(url, headers=self.__auth_header())

    def get_a_list_of_firewall_rules_by_server(self, subscription_id: str, resource_group_name: str, server_name: str):
        """Gets a list of firewall rules for a server."""
        url = (
            "https://management.azure.com/subscriptions/{0}/resourceGroups/{1}"
            "/providers/{2}/servers/{3}/firewallRules?api-version={4}"
        ).format(subscription_id, resource_group_name, self.PROVIDES, server_name, self.API_VERSION)
        return self.__session.get(url, headers=self.__auth_header())

    def creates_or_updates_a_firewall_rule(self, subscription_id: str, server_name: str, firewall_rule_name: str, body):
        """Creates or updates a firewall rule."""
        url = (
            "https://management.azure.com/subscriptions/{0}/resourceGroups/{1}"
            "/providers/{2}/servers/{3}/firewallRules/{4}?api-version={5}"
        ).format(subscription_id, self.__resource_group, self.PROVIDES, server_name, firewall_rule_name, self.API_VERSION)
        return self.__session.put(url, headers=self.__auth_header(content_type=True), json=body)
