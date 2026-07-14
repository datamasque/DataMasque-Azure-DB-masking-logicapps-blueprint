import logging
import json
import azure.functions as func
import os
from ..services.providers.microsoft_sql import MicrosoftSQL

subscription_id = os.environ['SUBSCRIPTION_ID']
resource_group = os.environ['RESOURCE_GROUP']
tenant_id = os.environ['TENANT_ID']
client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']
database_id = os.environ['DATABASE_ID']


def _summarise(database):
    return {
        "location": database['location'],
        "sku": database['sku'],
        "id": database['id'],
        "name": database['name'],
    }


def checkDatabase(databases):
    # Ignore databases still being created (no creationDate / not Online) and
    # the implicit 'master' system database; guard against an empty result.
    candidates = [
        db for db in databases
        if db.get('name') != 'master' and db.get('properties', {}).get('creationDate')
    ]
    if not candidates:
        raise ValueError("No ready source database found on the Azure SQL server")

    candidates.sort(key=lambda x: x['properties']['creationDate'], reverse=True)

    # Prefer the database matching the configured database_id, else the newest.
    for database in candidates:
        if database['properties'].get('databaseId') == database_id:
            return _summarise(database)
    return _summarise(candidates[0])

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Fetch database with the latest creation time in the source Azure SQL server (single database)')

    # get content of body request
    req_body = req.get_json()
    
    sql_service = MicrosoftSQL(tenant_id, client_id, client_secret, resource_group)

    source_db_instance_identifier = req_body.get('DBInstanceIdentifier')
    resource_group_source = req_body.get('ResourceGroup', resource_group)
    DATAMASQUE_CONNECTION_ID = req_body.get('DATAMASQUE_CONNECTION_ID')
    DATAMASQUE_RULESET_ID = req_body.get('DATAMASQUE_RULESET_ID')

    # Gets a list of databases in the source Azure SQL database
    res = sql_service.get_list_of_databases_from_server(subscription_id, resource_group_source, source_db_instance_identifier)
    if res.status_code != 200:
        # Surface the upstream error and propagate its status so the workflow
        # fails fast rather than dereferencing a missing 'value'.
        return func.HttpResponse(json.dumps(res.json()), mimetype="application/json", status_code=res.status_code)

    databases = list(res.json().get('value', []))
    result = checkDatabase(databases)
    data = {
        "DBSnapshotIdentifier": result,
        "DBInstanceIdentifier": source_db_instance_identifier,
        "SubscriptionID": subscription_id,
        "ResourceGroup": resource_group_source,
        "DATAMASQUE_CONNECTION_ID": DATAMASQUE_CONNECTION_ID,
        "DATAMASQUE_RULESET_ID": DATAMASQUE_RULESET_ID
    }

    return func.HttpResponse(json.dumps(data), mimetype="application/json", status_code=res.status_code)
