import logging
import json
import os
import azure.functions as func
from ..services.providers import MicrosoftSQL
from ..services.credentials import service_principal

resource_group = os.environ['RESOURCE_GROUP']

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Get all the public ip addresses in the source Azure SQL Server's firewall")

    # get content of body request
    req_body = req.get_json()
    tenant_id, client_id, secret = service_principal(req_body)
    DATAMASQUE_CONNECTION_ID = req_body.get('DATAMASQUE_CONNECTION_ID')
    DATAMASQUE_RULESET_ID = req_body.get('DATAMASQUE_RULESET_ID')
    sql_service = MicrosoftSQL(tenant_id, client_id, secret, resource_group)
            
    subscription_id = req_body.get('SubscriptionID')
    resource_group_source = req_body.get('ResourceGroup')

    source_db_instance_identifier = req_body.get('DBInstanceIdentifier')
    db_snapshot_identifier = req_body.get('DBSnapshotIdentifier')
    
    res = sql_service.get_a_list_of_firewall_rules_by_server(subscription_id, resource_group_source, source_db_instance_identifier.get('name'))
    if res.status_code == 200:
        value = []
        for ipaddress in res.json().get('value'):
            start_ip = ipaddress.get('properties').get('startIpAddress', None)
            end_ip = ipaddress.get('properties').get('endIpAddress', None)
            if start_ip is None or end_ip is None:
                continue
            
            value.append({ "name": f'{ipaddress.get("name")}', "properties": ipaddress.get('properties') })
        
    data = {
        "DBInstanceIdentifier": source_db_instance_identifier.get('name') + "-datamasque",
        "DBSnapshotIdentifier": db_snapshot_identifier,
        "FirewallRules": res.json() if res.status_code != 200 else json.dumps(value),
        "SubscriptionID": subscription_id,
        "ResourceGroup": resource_group_source,
        "DATAMASQUE_CONNECTION_ID": DATAMASQUE_CONNECTION_ID,
        "DATAMASQUE_RULESET_ID": DATAMASQUE_RULESET_ID
    }

    return func.HttpResponse(json.dumps(data), mimetype="application/json", status_code=res.status_code)
