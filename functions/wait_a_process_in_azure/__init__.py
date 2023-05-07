import logging
import json
import os
import azure.functions as func
from ..services.providers import MicrosoftSQL

resource_group = os.environ['RESOURCE_GROUP']

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Check progress status in Azure')

    # get content of body request
    req_body = req.get_json()
    tenant_id = req_body.get('TenantID')
    client_id = req_body.get('ClientID')
    secret = req_body.get('ClientSecret')
    sql_service = MicrosoftSQL(tenant_id, client_id, secret, resource_group)
    
    message_queue = req_body.get('MessageQueue')
    
    res = sql_service.get_status_process(message_queue)
    
    return func.HttpResponse(json.dumps(res.json()), mimetype="application/json", status_code=res.status_code)
