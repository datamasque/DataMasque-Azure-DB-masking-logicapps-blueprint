import logging
import json
import os
import azure.functions as func
from ..services.providers import MicrosoftSQL

resource_group = os.environ['RESOURCE_GROUP']

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('A database copy is a transactionally consistent snapshot of the source database as of a point in time after the copy request is initialed')

    # get content of body request
    req_body = req.get_json()
    tenant_id = req_body.get('TenantID')
    client_id = req_body.get('ClientID')
    secret = req_body.get('ClientSecret')
    DATAMASQUE_CONNECTION_ID = req_body.get('DATAMASQUE_CONNECTION_ID')
    DATAMASQUE_RULESET_ID = req_body.get('DATAMASQUE_RULESET_ID')
    sql_service = MicrosoftSQL(tenant_id, client_id, secret, resource_group)
            
    subscription_id = req_body.get('SubscriptionID')

    source_db_instance_identifier = req_body.get('DBInstanceIdentifier')
    db_snapshot_identifier = req_body.get('DBSnapshotIdentifier')
    
    # configure from the configuration of the source Azure SQL database
    body = {
        "location": db_snapshot_identifier['location'],
        "sku": db_snapshot_identifier['sku'],
        "properties": {
            "createMode": "Copy",
            "sourceDatabaseId": db_snapshot_identifier['id']
        }
    }
    
    res = sql_service.create_or_update_database(subscription_id, source_db_instance_identifier, db_snapshot_identifier['name'], body)
    data = {
        "MessageQueue": res.json() if str(res.status_code)[0:1] != "2" else dict(res.headers).get('Azure-AsyncOperation', ""),
        "DBInstanceIdentifier": source_db_instance_identifier,
        "DBSnapshotIdentifier": db_snapshot_identifier,
        "SubscriptionID": subscription_id,
        "ResourceGroup": req_body.get('ResourceGroup'),
        "TenantID": tenant_id,
        "ClientID": client_id,
        "ClientSecret": secret,
        "DATAMASQUE_CONNECTION_ID": DATAMASQUE_CONNECTION_ID,
        "DATAMASQUE_RULESET_ID": DATAMASQUE_RULESET_ID
    }
    
    return func.HttpResponse(json.dumps(data), mimetype="application/json", status_code=res.status_code)

