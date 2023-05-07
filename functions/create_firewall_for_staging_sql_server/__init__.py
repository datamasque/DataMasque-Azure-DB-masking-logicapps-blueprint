import logging
import json
import os
import azure.functions as func
from ..services.providers import MicrosoftSQL

resource_group = os.environ['RESOURCE_GROUP']

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Create a firewall rule for the staging Azure SQL server')

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
    firewall_rules = req_body.get('FirewallRules')
    
    is_allow_access = False
    # add ipaddress from the source Azure SQL server network
    for firewall in json.loads(firewall_rules):
        if firewall.get("properties").get("startIpAddress") == "0.0.0.0":
            is_allow_access = True
            
        res = sql_service.creates_or_updates_a_firewall_rule(subscription_id, source_db_instance_identifier, firewall.get("name"), { "properties": firewall.get("properties")})
    
    if not is_allow_access:
        # add ipaddress 0.0.0.0 for allow azure services and resources to access this server
        body = {
            "properties": {
                "startIpAddress": "0.0.0.0",
                "endIpAddress": "0.0.0.0"
            }
        }
            
        res = sql_service.creates_or_updates_a_firewall_rule(subscription_id, source_db_instance_identifier, "default", body)
    
    data = {
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
