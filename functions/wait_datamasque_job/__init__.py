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

def login(base_url, username, password):
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
    data = {'username' : username, 'password': password}
    response = requests.post(base_url+api, data=data, verify=False)
    
    return response.json()

def runs(base_url, token, run_id=None):
    """
    Read all the run logs
    Can also use the same URL followed by the 'id' to only get info about that connection
    ex: 'https://masque.local/api/runs/6659eaef-f821-4e96-a659-cd3ff73f7a02/'
    full_url = 'https://masque.local/api/runs/'
    method = 'GET'
    headers = {'Authorization': 'Token ' + 'your_user_token'}
    data parameters:
       None
    status_code[200] == Success
    return json:
        {
         'id': 180,
         'name': 'test_run',
         'status': 'failed',
         'connection': 'some_connection_id',
         'connection_name': 'new_postgres',
         'ruleset': 'some_ruleset_id',
         'ruleset_name': 'test_ruleset',
         'created_time': '2022-02-24T22:52:58.233400Z',
         'start_time': '2022-02-24T22:53:00.291878Z',
         'end_time': '2022-02-24T22:53:01.501147Z',
         'options': {'dry_run': False, 'buffer_size': 10000, 'continue_on_failure': False, 'run_secret': None},
         'has_sdd_report': False
         }
    """
    if run_id:
        api = 'api/runs/{}/'.format(run_id)
    else:
        api = 'api/runs/'
    response = requests.get(base_url+api, headers=token, verify=False)
    
    return response

def check_run(run_id):
    # retrieving your secret
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=datamasque_keyvault, credential=credential)
    retrieved_secret = client.get_secret(secret_name)

    user_username = json.loads(retrieved_secret.value).get('username')
    user_password = json.loads(retrieved_secret.value).get('password')

    user_login_res = login(base_url, user_username, user_password)
    user_token = {'Authorization': 'Token ' + user_login_res['key']}

    return runs(base_url, user_token, run_id) # replace '180' with some run id

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Check progress status in DataMasque')
    # get content of body request
    req_body = req.get_json()
    
    res = check_run(req_body.get('RunID'))
    if res.status_code == 200:
        status = res.json().get('status')
        if status == 'failed' or status == 'cancelled':
            return func.HttpResponse(json.dumps(res.json()), mimetype="application/json", status_code=500)

    return func.HttpResponse(json.dumps(res.json()), mimetype="application/json", status_code=res.status_code)
