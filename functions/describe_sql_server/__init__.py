import logging
import json
import os
import azure.functions as func
from ..services.providers.microsoft_sql import MicrosoftSQL

resource_group = os.environ['RESOURCE_GROUP']

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Fetch the configuration of the source Azure SQL server')

    # get content of body request
    req_body = req.get_json()
    tenant_id = req_body.get('TenantID')
    client_id = req_body.get('ClientID')
    secret = req_body.get('ClientSecret')
    sql_service = MicrosoftSQL(tenant_id, client_id, secret, resource_group)
            
    subscription_id = req_body.get('SubscriptionID')
    resource_group_source = req_body.get('ResourceGroup')
    
    source_db_instance_identifier = req_body.get('DBInstanceIdentifier')
    DATAMASQUE_CONNECTION_ID = req_body.get('DATAMASQUE_CONNECTION_ID')
    DATAMASQUE_RULESET_ID = req_body.get('DATAMASQUE_RULESET_ID')
    # fetch the configuration of the source Azure SQL server
    res = sql_service.get_configuration_sql_server(subscription_id, resource_group_source, source_db_instance_identifier)
    if res.status_code == 200:
        server = res.json()
        source_db_instance_identifier = {
            "location": server['location'],
            "name": server['name'],
            "properties": server['properties']
        }

    data = {
        "DBInstanceIdentifier": res.json() if res.status_code != 200 else source_db_instance_identifier,
        "DBSnapshotIdentifier": req_body.get('DBSnapshotIdentifier'),
        "SubscriptionID": subscription_id,
        "ResourceGroup": resource_group_source,
        "TenantID": tenant_id,
        "ClientID": client_id,
        "ClientSecret": secret,
        "DATAMASQUE_CONNECTION_ID": DATAMASQUE_CONNECTION_ID,
        "DATAMASQUE_RULESET_ID": DATAMASQUE_RULESET_ID
    }
    
    return func.HttpResponse(json.dumps(data), mimetype="application/json", status_code=res.status_code)
