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

def checkDatabase(databases):
    databaseResult = {}
    hasDatabaseId = False
    databases.sort(key=lambda x: x['properties']['creationDate'], reverse=True)
    for database in databases:
        if(database['properties']['databaseId'] == database_id):
            hasDatabaseId =True
            databaseResult = {
                "location": database['location'],
                "sku": database['sku'],
                "id": database['id'],
                "name": database['name']
            }
    if(not hasDatabaseId):
        databaseResult = {
                "location": databases[0]['location'],
                "sku": databases[0]['sku'],
                "id": databases[0]['id'],
                "name": databases[0]['name']
            }
    return databaseResult

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
    if res.status_code == 200:
        databases = list(res.json()['value'])
        result = checkDatabase(databases)
    data = {
        "DBSnapshotIdentifier": res.json() if res.status_code != 200 else result,
        "DBInstanceIdentifier": source_db_instance_identifier,
        "SubscriptionID": subscription_id,
        "ResourceGroup": resource_group_source,
        "TenantID": tenant_id,
        "ClientID": client_id,
        "ClientSecret": client_secret,
        "DATAMASQUE_CONNECTION_ID": DATAMASQUE_CONNECTION_ID,
        "DATAMASQUE_RULESET_ID": DATAMASQUE_RULESET_ID
    }
    
    return func.HttpResponse(json.dumps(data), mimetype="application/json", status_code=res.status_code)
