import requests

from ..token import Token

class MicrosoftSQL:
    PROVIDES = "Microsoft.Sql"
    API_VERSION = "2021-11-01-preview"
    
    def __init__(self, tenant_id: str, client_id: str, secret: str, resource_group: str):
        self.__token = Token(tenant_id=tenant_id, client_id=client_id, secret=secret)
        self.__resource_group = resource_group
    
    def get_status_process(self, azure_async_operation: str):
        """Gets a status of process in Azure Cloud

        Args:
            azure_async_operation (str): The url is a address of a operations 

        Raises:
            ex: throw exception

        Returns:
            Response: object
        """
        try:
            res = requests.get(url=azure_async_operation, headers= {'Authorization': f'Bearer {self.__token.get_access_token()}'})
            
            return res
        except BaseException as ex:
            raise ex
        
    
    def get_configuration_sql_server(self, subscription_id: str, resource_group_name: str, server_name: str):
        """Get configuration a server

        Args:
            subscription_id (str): The subscription ID that identifies an Azure subscription.
            resource_group_name (str): The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.
            server_name (str): The name of the server.

        Raises:
            ex: throw exception

        Returns:
            Response: Server
        """
        try:
            URL_FORMAT = "https://management.azure.com/subscriptions/{0}/resourceGroups/{1}/providers/{2}/servers/{3}?api-version={4}"
            url = URL_FORMAT.format(subscription_id, resource_group_name, self.PROVIDES, server_name, self.API_VERSION)
            res = requests.get(url, headers= {'Authorization': f'Bearer {self.__token.get_access_token()}'})
            
            return res
        except BaseException as ex:
            raise ex
        
    def get_list_of_databases_from_server(self, subscription_id: str, resource_group_name: str, server_name: str):
        """Gets a list of databases.

        Args:
            subscription_id (str): The subscription ID that identifies an Azure subscription.
            resource_group_name (str): The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.
            server_name (str): The name of the server.

        Raises:
            ex: throw exception

        Returns:
            Response: DatabaseListResult
        """
        try:
            URL_FORMAT = "https://management.azure.com/subscriptions/{0}/resourceGroups/{1}/providers/{2}/servers/{3}/databases?api-version={4}"
            url = URL_FORMAT.format(subscription_id, resource_group_name, self.PROVIDES, server_name, self.API_VERSION)
            res = requests.get(url, headers= {'Authorization': f'Bearer {self.__token.get_access_token()}'})
                        
            return res
        except BaseException as ex:
            raise ex
        
    def creates_or_updates_server(self, subscription_id: str, server_name: str, body):
        """Creates or updates a server

        Args:
            subscription_id (str): The subscription ID that identifies an Azure subscription.
            resource_group_name (str): The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.
            server_name (str): The name of the server.
            body (object): Body request
            
        Raises:
            ex: throw exception
        
        Returns:
            Response: Server
        """
        try:
            URL_FORMAT = "https://management.azure.com/subscriptions/{0}/resourceGroups/{1}/providers/{2}/servers/{3}?api-version={4}"
            url = URL_FORMAT.format(subscription_id, self.__resource_group, self.PROVIDES, server_name, self.API_VERSION)
            headers = {
                "Authorization": f'Bearer {self.__token.get_access_token()}',
                "Content-Type": "application/json"
            }
            
            res = requests.put(url, headers=headers, json=body)
            return res
        except BaseException as ex:
            raise ex
        
    def create_or_update_database(self, subscription_id: str, server_name: str, database_name: str, body):
        """Creates a new database or updates an existing database.

        Args:
            subscription_id (str): The subscription ID that identifies an Azure subscription.
            resource_group_name (str): The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.
            server_name (str): The name of the server.
            database_name (str): The name of the database.
            body (object): Body request

        Raises:
            ex: throw exception

        Returns:
            Response: Database
        """
        try:
            URL_FORMAT = "https://management.azure.com/subscriptions/{0}/resourceGroups/{1}/providers/{2}/servers/{3}/databases/{4}?api-version={5}"
            url = URL_FORMAT.format(subscription_id, self.__resource_group, self.PROVIDES, server_name, database_name, self.API_VERSION)
            headers = {
                "Authorization": f'Bearer {self.__token.get_access_token()}',
                "Content-Type": "application/json"
            }
            
            res = requests.put(url, headers=headers, json=body)
            return res
        except BaseException as ex:
            raise ex
        
        
    def export_database_to_blod_storage(self, subscription_id: str, server_name: str, database_name: str, body):
        """Exports a database to blod storage

        Args:
            subscription_id (str): The subscription ID that identifies an Azure subscription.
            resource_group_name (str): The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.
            server_name (str): The name of the server.
            database_name (str): The name of the database.
            body (object): Body request

        Raises:
            ex: throw exception

        Returns:
            Response: ImportExportOperationResult
        """
        try:
            URL_FORMAT = "https://management.azure.com/subscriptions/{0}/resourceGroups/{1}/providers/{2}/servers/{3}/databases/{4}/export?api-version={5}"
            url = URL_FORMAT.format(subscription_id, self.__resource_group, self.PROVIDES, server_name, database_name, self.API_VERSION)
            headers = {
                "Authorization": f'Bearer {self.__token.get_access_token()}',
                "Content-Type": "application/json"
            }
            
            res = requests.post(url, headers=headers, json=body)
            return res
        except BaseException as ex:
            raise ex
        
    def delete_server(self, subscription_id: str, server_name: str):
        """Deletes a server.

        Args:
            subscription_id (str): The subscription ID that identifies an Azure subscription.
            resource_group_name (str): The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.
            server_name (str): The name of the server.

        Raises:
            ex: throw exception

        Returns:
            Response: object
        """
        try:
            URL_FORMAT = "https://management.azure.com/subscriptions/{0}/resourceGroups/{1}/providers/{2}/servers/{3}?api-version={4}"
            url = URL_FORMAT.format(subscription_id, self.__resource_group, self.PROVIDES, server_name, self.API_VERSION)
            res = requests.delete(url, headers={ "Authorization": f'Bearer {self.__token.get_access_token()}' })
            
            return res
        except BaseException as ex:
            raise ex
        
    def get_a_list_of_firewall_rules_by_server(self, subscription_id: str, resource_group_name: str, server_name: str):
        """Gets a list of firewall rules.

        Args:
            subscription_id (str): The subscription ID that identifies an Azure subscription.
            resource_group_name (str): The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.
            server_name (str): The name of the server.

        Raises:
            ex: throw exception

        Returns:
            Response: FirewallRuleListResult
        """
        try:
            URL_FORMAT = "https://management.azure.com/subscriptions/{0}/resourceGroups/{1}/providers/{2}/servers/{3}/firewallRules?api-version={4}"
            url = URL_FORMAT.format(subscription_id, resource_group_name, self.PROVIDES, server_name, self.API_VERSION)
            res = requests.get(url, headers={ "Authorization": f'Bearer {self.__token.get_access_token()}' })
            
            return res
        except BaseException as ex:
            raise ex
        
    def creates_or_updates_a_firewall_rule(self, subscription_id: str, server_name: str, firewall_rule_name: str, body):
        """Creates or updates a firewall rule.

        Args:
            subscription_id (str): The subscription ID that identifies an Azure subscription.
            resource_group_name (str): The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.
            server_name (str): The name of the server.
            firewall_rule_name (str): The name of the firewall rule.
            body (object): { properties.endIpAddress, properties.startIpAddress }

        Raises:
            ex: throw exception

        Returns:
            Response: FirewallRule
        """
        try:
            URL_FORMAT = "https://management.azure.com/subscriptions/{0}/resourceGroups/{1}/providers/{2}/servers/{3}/firewallRules/{4}?api-version={5}"
            url = URL_FORMAT.format(subscription_id, self.__resource_group, self.PROVIDES, server_name, firewall_rule_name, self.API_VERSION)
            headers = {
                "Authorization": f'Bearer {self.__token.get_access_token()}',
                "Content-Type": "application/json"
            }
            
            res = requests.put(url, headers=headers, json=body)
            return res
        except BaseException as ex:
            raise ex