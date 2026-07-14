import logging
import json
import os
import azure.functions as func
from ..services.providers import MicrosoftSQL
from ..services.credentials import service_principal

resource_group = os.environ['RESOURCE_GROUP']

# By default the staging server only inherits the source server's firewall rules
# (the IPs DataMasque already reaches). Set ALLOW_AZURE_SERVICES=true to also add
# the special 0.0.0.0 "Allow Azure services" rule if your topology needs it.
allow_azure_services = os.environ.get('ALLOW_AZURE_SERVICES', 'false').strip().lower() in ('true', '1', 'yes')

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Create a firewall rule for the staging Azure SQL server')

    # get content of body request
    req_body = req.get_json()
    tenant_id, client_id, secret = service_principal(req_body)
    DATAMASQUE_CONNECTION_ID = req_body.get('DATAMASQUE_CONNECTION_ID')
    DATAMASQUE_RULESET_ID = req_body.get('DATAMASQUE_RULESET_ID')
    sql_service = MicrosoftSQL(tenant_id, client_id, secret, resource_group)
            
    subscription_id = req_body.get('SubscriptionID')

    source_db_instance_identifier = req_body.get('DBInstanceIdentifier')
    db_snapshot_identifier = req_body.get('DBSnapshotIdentifier')
    firewall_rules = req_body.get('FirewallRules')
    
    has_allow_azure_rule = False
    # Replicate the source Azure SQL server's firewall rules onto the staging
    # server, so only the IPs already trusted by the source can reach the clone.
    for firewall in json.loads(firewall_rules):
        if firewall.get("properties").get("startIpAddress") == "0.0.0.0":
            has_allow_azure_rule = True

        res = sql_service.creates_or_updates_a_firewall_rule(subscription_id, source_db_instance_identifier, firewall.get("name"), { "properties": firewall.get("properties")})

    if allow_azure_services and not has_allow_azure_rule:
        # Optional: the 0.0.0.0 rule is Azure SQL's special "Allow Azure services
        # and resources to access this server" rule (not 0.0.0.0/0 internet).
        body = {
            "properties": {
                "startIpAddress": "0.0.0.0",
                "endIpAddress": "0.0.0.0"
            }
        }

        res = sql_service.creates_or_updates_a_firewall_rule(subscription_id, source_db_instance_identifier, "AllowAzureServices", body)

    data = {
        "DBInstanceIdentifier": source_db_instance_identifier,
        "DBSnapshotIdentifier": db_snapshot_identifier,
        "SubscriptionID": subscription_id,
        "ResourceGroup": req_body.get('ResourceGroup'),
        "DATAMASQUE_CONNECTION_ID": DATAMASQUE_CONNECTION_ID,
        "DATAMASQUE_RULESET_ID": DATAMASQUE_RULESET_ID
    }

    return func.HttpResponse(json.dumps(data), mimetype="application/json", status_code=res.status_code)
