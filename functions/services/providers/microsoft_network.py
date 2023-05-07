import requests

from ..token import Token

class MicrosoftNetwork:
    PROVIDES = "Microsoft.Network"
    API_VERSION = "2021-08-01"
    
    def __init__(self, tenant_id: str, client_id: str, secret: str):
        self.__token = Token(tenant_id=tenant_id, client_id=client_id, secret=secret)
    
    def get_all_public_ip_addresses_in_resource_group(self, subscription_id: str, resource_group_name: str):
        """Gets all public IP addresses in a resource group

        Args:
            subscription_id (str): The subscription credentials which uniquely identify the Microsoft Azure subscription. The subscription ID forms part of the URI for every service call.
            resource_group_name (str): The name of the resource group.

        Raises:
            ex: throw exception

        Returns:
            Response: PublicIPAddressListResult
        """
        try:
            URL_FORMAT = "https://management.azure.com/subscriptions/{0}/resourceGroups/{1}/providers/{2}/publicIPAddresses?api-version={3}"
            url = URL_FORMAT.format(subscription_id, resource_group_name, self.PROVIDES, self.API_VERSION)
            
            res = requests.get(url, headers={ "Authorization": f'Bearer {self.__token.get_access_token()}' })
            return res
        except BaseException as ex:
            raise ex