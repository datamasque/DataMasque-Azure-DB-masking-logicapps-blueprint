import json
import logging
import os
import azure.functions as func
import datetime
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from ..services.providers import MicrosoftSQL

datamasque_keyvault = os.environ['DATAMASQUE_KEYVAULT']
secret_name = os.environ['SECRET_NAME']
resource_group = os.environ['RESOURCE_GROUP']

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Export a masked database to blob storage')

    # get content of body request
    req_body = req.get_json()
    tenant_id = req_body.get('TenantID')
    client_id = req_body.get('ClientID')
    secret = req_body.get('ClientSecret')
    sql_service = MicrosoftSQL(tenant_id, client_id, secret, resource_group)
    
    subscription_id = req_body.get('SubscriptionID')
    
    source_db_instance_identifier = req_body.get('DBInstanceIdentifier')
    db_snapshot_identifier = req_body.get('DBSnapshotIdentifier')
    
    # retrieving your secret
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=datamasque_keyvault, credential=credential)
    retrieved_secret = client.get_secret(secret_name)

    user_username = json.loads(retrieved_secret.value).get('administratorLogin')
    user_password = json.loads(retrieved_secret.value).get('administratorLoginPassword')
    database_name = db_snapshot_identifier.get('name')
    utc_datetime = datetime.datetime.utcnow()
    name_file = f'{database_name}_masked_{utc_datetime.strftime("%Y%m%d%H%M")}'
    body = {
        "storageKeyType": "StorageAccessKey",
        "storageKey": os.environ['STORAGE_KEY'],
        "storageUri": os.environ['STORAGE_URI'] + name_file + ".bacpac",
        "administratorLogin": user_username,
        "administratorLoginPassword": user_password,
        "authenticationType": "Sql"
    }
    
    res = sql_service.export_database_to_blod_storage(subscription_id, source_db_instance_identifier, database_name, body)
    data = {
        "MessageQueue": res.json() if str(res.status_code)[0:1] != "2" else dict(res.headers).get('Azure-AsyncOperation', ""),
        "DBInstanceIdentifier": source_db_instance_identifier,
        "SubscriptionID": subscription_id,
        "ResourceGroup": req_body.get('ResourceGroup'),
        "TenantID": tenant_id,
        "ClientID": client_id,
        "ClientSecret": secret
    }

    return func.HttpResponse(json.dumps(data), mimetype="application/json", status_code=res.status_code)
