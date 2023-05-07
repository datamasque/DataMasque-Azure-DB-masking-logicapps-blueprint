import logging
import azure.functions as func
import json
import os
from ..services.providers import MicrosoftSQL

resource_group = os.environ['RESOURCE_GROUP']

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Delete the staging Azure SQL server')
    # get content of body request
    req_body = req.get_json()
    tenant_id = req_body.get('TenantID')
    client_id = req_body.get('ClientID')
    secret = req_body.get('ClientSecret')
    sql_service = MicrosoftSQL(tenant_id, client_id, secret, resource_group)
    
    subscription_id = req_body.get('SubscriptionID')
    
    source_db_instance_identifier = req_body.get('DBInstanceIdentifier')
    
    res = sql_service.delete_server(subscription_id, source_db_instance_identifier)

    return func.HttpResponse(json.dumps(res.json()), mimetype="application/json", status_code=res.status_code)
