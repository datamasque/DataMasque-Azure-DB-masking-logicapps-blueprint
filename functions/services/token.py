import requests

class Token:
    def __init__(self, tenant_id: str, client_id: str, secret: str) -> None:
        self.__tenant_id = tenant_id
        self.__client_id = client_id
        self.__secret = secret
        
    def get_access_token(self) -> str:
        try:
            RESOURCE_URL = "https://management.azure.com/"
            TOKEN_URL = f"https://login.microsoftonline.com/{self.__tenant_id}/oauth2/token"
            GRANT_TYPE = "client_credentials"
            
            body_data = {
                'client_id': self.__client_id,
                'client_secret': self.__secret,
                'grant_type': GRANT_TYPE,
                'resource': RESOURCE_URL
            }
            
            res = requests.post(
                TOKEN_URL, data = body_data,
                headers= {"Content-Type": "application/x-www-form-urlencoded"})
            
            return res.json()["access_token"]
        except BaseException as e:
            raise e