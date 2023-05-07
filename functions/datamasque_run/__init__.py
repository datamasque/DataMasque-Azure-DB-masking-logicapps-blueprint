import os
import logging
import azure.functions as func
import requests
import json

from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

base_url = os.environ['DATAMASQUE_BASE_URL'] # change base url to the url of the DataMasque instance
datamasque_keyvault = os.environ['DATAMASQUE_KEYVAULT']
secret_name = os.environ['SECRET_NAME']

def login(base_url: str, username: str, password: str):
    """
    Login with username and password to get user_token
    which can be used for other API
    
    full_url = 'https://masque.local/api/auth/token/login/'
    method = 'POST'
    
    data parameters:
        'username': 'your_username',
        'password': 'your_password'
        
    status_code[200] == Success
    
    return json:
        {'id': 11,
         'key': '38e1befbdcbea57b838082e7d7612bee392d33e3',
         'client_ip': '172.18.0.1',
         'client_browser': 'Firefox',
         'client_os': 'Ubuntu',
         'client_device': 'Other',
         'date_time_created': '2022-02-13T21:36:23.468892Z',
         'date_time_expires': '2022-02-14T07:22:11.917111Z'}
    """
    api = 'api/auth/token/login/'
    data = {'username': username, 'password': password}
    response = requests.post(base_url+api, data=data, verify=False)
    
    return response.json()

def create_run(base_url, token, run_dict):
    """
    Create a run
    full_url = 'https://masque.local/api/runs/'
    method = 'POST'
    headers = {'Authorization': 'Token ' + 'your_user_token'}
    JSON parameters:
       {
        'name': 'run_name',
        'connection': 'connection_id',
        'ruleset': 'ruleset_id',
        'options': {
            'dry_run': False, 'buffer_size': 10000, 'continue_on_failure': False, 'run_secret': 'thisismynewrunsecret'
            }
       }
    status_code[201] == Success
    return json:
        {'id': xxx,
         'name': 'run_name',
         'status': 'queued',
         'connection': 'connection_id',
         'connection_name': 'connection_name',
         'ruleset': 'ruleset_id',
         'ruleset_name': 'ruleset_name',
         'created_time': '2022-02-15T02:01:33.012798Z',
         'start_time': None,
         'end_time': None,
         'options': {'dry_run': False, 'buffer_size': 10000, 'continue_on_failure': False, 'run_secret': ''},
         'has_sdd_report': False
         }
    """
    api = 'api/runs/'
    response = requests.post(base_url+api, json=run_dict, headers=token, verify=False)
    
    return response

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Create a masking job based on the connection id and ruleset provided')
    # get content of body request
    req_body = req.get_json()
    DATAMASQUE_CONNECTION_ID = req_body.get('DATAMASQUE_CONNECTION_ID')
    DATAMASQUE_RULESET_ID = req_body.get('DATAMASQUE_RULESET_ID')
    # retrieving your secret
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=datamasque_keyvault, credential=credential)
    retrieved_secret = client.get_secret(secret_name)

    user_username = json.loads(retrieved_secret.value).get('username')
    user_password = json.loads(retrieved_secret.value).get('password')
    
    user_login_res = login(base_url, user_username, user_password)
    token = {'Authorization': 'Token ' + user_login_res['key']}
    run_dict = {
        'name': 'datamasque_blueprint',
        'connection': DATAMASQUE_CONNECTION_ID,
        'ruleset': DATAMASQUE_RULESET_ID,
        'options': {
            'dry_run': False, 'buffer_size': 10000, 'continue_on_failure': False, 'run_secret': 'thisismynewrunsecret'
        }
    }
    
    res = create_run(base_url, token, run_dict)
    data = {
        "RunID": res.json().get('id', None),
        "DBInstanceIdentifier": req_body.get('DBInstanceIdentifier'),
        "DBSnapshotIdentifier": req_body.get('DBSnapshotIdentifier'),
        "SubscriptionID": req_body.get('SubscriptionID'),
        "ResourceGroup": req_body.get('ResourceGroup'),
        "TenantID": req_body.get('TenantID'),
        "ClientID": req_body.get('ClientID'),
        "ClientSecret": req_body.get('ClientSecret')
    }

    return func.HttpResponse(json.dumps(data), mimetype="application/json", status_code=res.status_code)

