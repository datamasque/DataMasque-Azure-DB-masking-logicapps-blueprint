# Terraform Azure
## Introduction
The diagram below describes the DataMasque reference architecture in Azure. This blueprint can be used to create backup copy of masked production Azure SQL database which then can be used to provision the masked non-production database.

![Reference deployment](../create_masked_sqldatabase.png "Reference deployment")

Following Azure resources will be provisioned by the blueprint:
* Azure Logic App
* Azure Function App
* Azure Storage Account

## Deployment
### Prerequisites
* Active Azure Subscription with a User account that has **owner role** in it.
* Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
* Python runtime 3.9.7 installed.
* A DataMasque instance.
* Azure SQL server and SQL database (source database).
* DataMasque `connection id` and `ruleset id`.

### Step-by-step process to deploy the logic app.
###### Store the DataMasque instance credentials and account login Azure SQL server in Azure Key vault.
The secret need to follow the format as below :
```json
{
  "administratorLogin": "sqlserveradmin",
  "administratorLoginPassword": "sqlserverpassword",
  "username": "datamasque",
  "password": "Example$P@ssword"
}
```
###### Capture values for following parameters used by the deployment process:
| Parameter                                                                                                              | Description                                                                                                                    |
|------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| SubscriptionId                                                                                                      | Azure Subscription id where the resources will be deployed.                                    |
| ResourceGroup                                                                                                      | Resource Group id where the resources will be deployed.                                  |
| DatamasqueBaseUrl                                                                                                      | DataMasque instance URL with the EC2's private IP, i.e. https://\<ec2-instance-private-ip>.                                    |
| DatamasqueKeyVault                                                                                                    | Azure Keyvault name.                                                                                   |
| SecretName                                                                                                    | Secret name contains DataMasque instance credentials. vault.                                                                                   |
| DatamasqueConnectionId                                                                                                 | DataMasque connection ID.                                                                                                      |
| DatamasqueRuleSetId                                                                                                    | DataMasque rulset ID.                                                                                                          |
| StorageUrl                                                                                                    | Storage Account Url.                                                                                                          |
| StorageKey                                                                                                    | Storage Account Key.                                                                                                          |

###### The blueprint relies on below network configurations to successfully complete the execution.
* Allow connectivity between the source Azure SQL server allow inbound connections from the DataMasque instance. The configuration will be replicated when creating the staging Azure SQL server.
* The DataMasque instance should allow inbound connections from the **datamasque_run**  and **wait_datamasque_job** functions.
* Grant permissions for Azure function to use the Key vault secret.
* Provides access key of Azure Storage allow inbound connections from Azure Function.

### Step Function Execution
#### Invoke an execution manually
You can execute the step function manually:
```json
{ "DBInstanceIdentifier": "source_sql_database", "ResouceGroup": "source_resource_group", "DATAMASQUE_CONNECTION_ID": "20f5436c-74a5-4a08-8e12-0c00f5f2787a", "DATAMASQUE_RULESET_ID": "d0725d9d-c7bf-4736-863d-a994c0f3f8e3" }
```
The DataMasque connection ID provided in above json **must** not be configured to connect to the production database.

#### Schedule data masking execution
Creates a Logic App that shedules a trigger once a week which is disabled by default.
```json
"triggers": {
    "Recurrence": {
        "evaluatedRecurrence": {
            "frequency": "Day",
            "interval": 7
        },
        "recurrence": {
            "frequency": "Day",
            "interval": 7
        },
        "type": "Recurrence"
    }
}
```
###### Notes:
* The staging SQL server will have the same SQL server name schema as the source database with a `-datamasque` sufix:

| SQL server         | Endpoint                                                                    |
|----------------------|-----------------------------------------------------------------------------|
| Source SQL server  | ``source-sql``.database.windows.net       |
| Staging SQL server | ``source-sql-datamasque``.database.windows.net |

* The Azure SQL server username, password is obtained from Azure Key Vault.
* The staging Azure SQL server instance created by the function app will be deleted after the execution finishes.
* The masked Azure SQL database backup created by the function app will be preserved at the end of the execution.

### Azure Function definition
The following table describes the states and details of the step function definition.

| Step                     | Description                                                           |
|--------------------------|-----------------------------------------------------------------------|
| Describe source database | Fetch database with the latest creation time in the target Azure SQL server (single database)|
| Describe SQL server    | Fetch the configuration of the target Azure SQL server                   |
| Create staging SQL server | Create a staging Azure SQL server from the configuration of the target Azure SQL server             |
| Wait      | Until staging SQL server is being created                                |
| Describe network       | Get all public ip addresses in resource group |
| Create Firewall for staging SQL server          | Create a firewall rule for the staging Azure SQL server          |
| Copy source database to the staging SQL server         | A database copy is a transactionally consistent snapshot of the source database as of a point in time after the copy request is initialed                     |
| Wait        | Until database copy is in progress                             |
| Datamasque API run         | Create a masking job based on the connection id and ruleset provided                                   |
| Wait    | Until masking job is completed                                   |
| Export masking database         | Export a masking database to blob storage                                   |
| Wait a        | Until database export to blob storage is in progress                                   |
| Delete staging sql server         | Delete the staging Azure SQL server                                   |

![Azure function definition](workflow_logicapp.png "Azure Step function")