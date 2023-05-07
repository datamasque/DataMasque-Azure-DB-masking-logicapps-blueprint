import logging
import json
import os
import azure.functions as func
from ..services.providers.microsoft_sql import MicrosoftSQL

from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

datamasque_keyvault = os.environ['DATAMASQUE_KEYVAULT']
secret_name = os.environ['SECRET_NAME']
resource_group = os.environ['RESOURCE_GROUP']

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Create a staging Azure SQL server from the configuration of the source Azure SQL server')

    # get content of body request
    req_body = req.get_json()
    tenant_id = req_body.get('TenantID')
    client_id = req_body.get('ClientID')
    secret = req_body.get('ClientSecret')
    sql_service = MicrosoftSQL(tenant_id, client_id, secret, resource_group)
            
    subscription_id = req_body.get('SubscriptionID')
    
    source_db_instance_identifier = req_body.get('DBInstanceIdentifier')
    DATAMASQUE_CONNECTION_ID = req_body.get('DATAMASQUE_CONNECTION_ID')
    DATAMASQUE_RULESET_ID = req_body.get('DATAMASQUE_RULESET_ID')
    # retrieving your secret
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=datamasque_keyvault, credential=credential)
    retrieved_secret = client.get_secret(secret_name)

    user_username = json.loads(retrieved_secret.value).get('administratorLogin')
    user_password = json.loads(retrieved_secret.value).get('administratorLoginPassword')

    # configure from the configuration of the source Azure SQL server
    body = {
        "location": source_db_instance_identifier['location'],
        "properties": {
            "administratorLogin": user_username,
            "administratorLoginPassword": user_password,
            "administrators": source_db_instance_identifier['properties'].get('administrators', {}),
            "privateEndpointConnections": list(source_db_instance_identifier['properties'].get('privateEndpointConnections', [])),
            "publicNetworkAccess": source_db_instance_identifier['properties'].get('publicNetworkAccess', "Disabled"),
            "restrictOutboundNetworkAccess": source_db_instance_identifier['properties'].get('restrictOutboundNetworkAccess', "Disabled"),
            "version": source_db_instance_identifier['properties']['version']
        }
    }
    
    res = sql_service.creates_or_updates_server(subscription_id, source_db_instance_identifier['name'] + "-datamasque", body)
    data = {
        "MessageQueue": res.json() if str(res.status_code)[0:1] != "2" else dict(res.headers).get('Azure-AsyncOperation', ""),
        "DBInstanceIdentifier": source_db_instance_identifier,
        "DBSnapshotIdentifier": req_body.get('DBSnapshotIdentifier'),
        "SubscriptionID": subscription_id,
        "ResourceGroup": req_body.get('ResourceGroup'),
        "TenantID": tenant_id,
        "ClientID": client_id,
        "ClientSecret": secret,
        "DATAMASQUE_CONNECTION_ID": DATAMASQUE_CONNECTION_ID,
        "DATAMASQUE_RULESET_ID": DATAMASQUE_RULESET_ID
    }
    
    return func.HttpResponse(json.dumps(data), mimetype="application/json", status_code=res.status_code)
