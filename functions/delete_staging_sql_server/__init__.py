import logging
import azure.functions as func
import json
import os
from ..services.providers import MicrosoftSQL
from ..services.credentials import service_principal

resource_group = os.environ['RESOURCE_GROUP']

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Delete the staging Azure SQL server')
    # get content of body request
    req_body = req.get_json()
    tenant_id, client_id, secret = service_principal(req_body)
    sql_service = MicrosoftSQL(tenant_id, client_id, secret, resource_group)
    
    subscription_id = req_body.get('SubscriptionID')
    
    source_db_instance_identifier = req_body.get('DBInstanceIdentifier')
    
    res = sql_service.delete_server(subscription_id, source_db_instance_identifier)

    # A successful DELETE (200/202/204) often has an empty body; don't blow up
    # parsing JSON during cleanup.
    try:
        body = res.json()
    except ValueError:
        body = {"status_code": res.status_code}

    return func.HttpResponse(json.dumps(body), mimetype="application/json", status_code=res.status_code)
