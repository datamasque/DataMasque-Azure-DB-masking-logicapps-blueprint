locals {
  # Directories start with "C:..." on Windows; All other OSs use "/" for root.
  is_windows = substr(pathexpand("~"), 0, 1) == "/" ? false : true
}

resource "random_id" "rng" {
  keepers = {
    first = "${timestamp()}"
  }
  byte_length = 8
}

resource "azurerm_resource_group" "rg" {
  name     = "${var.prefix}rg-${random_id.rng.hex}"
  location = var.resource_group_location
}

resource "azurerm_template_deployment" "deploy-storage" {
  name                = "deploy-storage-${random_id.rng.hex}"
  resource_group_name = azurerm_resource_group.rg.name

  template_body = file("arm_templates/storage_accounts.json")

  parameters = {
    "storageAccountsNamePrefix" = "${var.prefix}${var.storage_accounts_name_prefix}"
    "containerName"             = "${var.container_name}"
    "location"                  = azurerm_resource_group.rg.location
  }

  deployment_mode = "Incremental"
}

resource "azurerm_template_deployment" "deploy-serverfarms" {
  name                = "deploy-serverfarms-${random_id.rng.hex}"
  resource_group_name = azurerm_resource_group.rg.name

  template_body = file("arm_templates/server_farms.json")
  parameters = {
    "serverfarmsNamePrefix" = "${var.prefix}-${var.serverfarms_name_prefix}"
    "location"              = azurerm_resource_group.rg.location
  }

  deployment_mode = "Incremental"
}

resource "azurerm_template_deployment" "deploy-functionapp" {
  name                = "deploy-functionapp-${random_id.rng.hex}"
  resource_group_name = azurerm_resource_group.rg.name

  template_body = file("arm_templates/functionapp.json")

  parameters = {
    "functionAppNamePrefix"   = "${var.prefix}-${var.function_app_name_prefix}"
    "location"                = azurerm_resource_group.rg.location
    "serverfarmsExternalID"   = "${azurerm_template_deployment.deploy-serverfarms.outputs["serverfarmsExternalID"]}"
    "storageAccountName"      = "${azurerm_template_deployment.deploy-storage.outputs["storageAccountName"]}"
    "storageBlobUri"          = "${azurerm_template_deployment.deploy-storage.outputs["storageBlobUri"]}"
    "storageAccountAccessKey" = "${azurerm_template_deployment.deploy-storage.outputs["storageAccountAccessKey"]}"
    "subscriptionID"          = "${var.subscription_id}"
    "tenantID"                = "${var.tenant}"
    "clientID"                = "${var.appId}"
    "clientSecret"            = "${var.password}"
    "datamasqueBaseUrl"       = "${var.datamasque_base_url}"
    "datamasqueKeyVault"      = "${var.datamasque_keyvault}"
    "secretName"              = "${var.secret_name}"
    "keyvaultResourceGroup"   = "${var.keyvault_resource_group}"
    "databaseID"              = "${var.database_id}"
  }

  deployment_mode = "Incremental"

  depends_on = [
    azurerm_template_deployment.deploy-storage,
    azurerm_template_deployment.deploy-serverfarms
  ]
}

# This resource will destroy (potentially immediately) after null_resource.next
resource "null_resource" "previous" {
  depends_on = [
    azurerm_template_deployment.deploy-functionapp
  ]
}

resource "time_sleep" "wait_30_seconds" {
  depends_on = [null_resource.previous]

  create_duration = "30s"
}

# This resource will create (at least) 30 seconds after null_resource.previous
resource "null_resource" "next" {
  depends_on = [time_sleep.wait_30_seconds]
}

resource "null_resource" "publish-functionapp" {
  triggers = {
    functions = "${random_id.rng.hex}"
  }

  provisioner "local-exec" {
    command = "cd ../functions && func azure functionapp publish ${azurerm_template_deployment.deploy-functionapp.outputs["functionappName"]}"
  }

  depends_on = [
    null_resource.next
  ]
}

resource "azurerm_key_vault_access_policy" "key-vault-policy" {
  key_vault_id = azurerm_template_deployment.deploy-functionapp.outputs["keyVaultID"]
  tenant_id    = var.tenant
  object_id    = azurerm_template_deployment.deploy-functionapp.outputs["principalID"]

  secret_permissions = [
    "Get",
    "List"
  ]

  depends_on = [null_resource.publish-functionapp]
}

resource "azurerm_template_deployment" "deploy-logicapp" {
  name                = "deploy-logicapp-${random_id.rng.hex}"
  resource_group_name = azurerm_resource_group.rg.name

  template_body = file("arm_templates/logic_app_manually_trigger.json")

  parameters = {
    "workflowsNamePrefix"  = "${var.prefix}-${var.manual_trigger_name_prefix}"
    "functionAppName"      = "${azurerm_template_deployment.deploy-functionapp.outputs["functionappName"]}"
    "dbInstanceIdentifier" = "${var.source_db_instance_identifier}"
    "sourceResourceGroup"  = "${var.source_resource_group}"
    "DATAMASQUE_CONNECTION_ID" = "${var.datamasque_connection_id}"
    "DATAMASQUE_RULESET_ID"  = "${var.datamasque_ruleset_id}"
    "intervalTime"         = var.interval_time
    "location"             = azurerm_resource_group.rg.location
  }

  deployment_mode = "Incremental"
  depends_on      = [null_resource.publish-functionapp]
}

resource "azurerm_template_deployment" "deploy-logicapp-recurring" {
  name                = "deploy-logicapp-recurring-${random_id.rng.hex}"
  resource_group_name = azurerm_resource_group.rg.name

  template_body = file("arm_templates/logic_app_recurring_trigger.json")

  parameters = {
    "workflowsNamePrefix"  = "${var.prefix}-${var.recurring_trigger_name_prefix}"
    "httpTrigger"          = "${azurerm_template_deployment.deploy-logicapp.outputs["httpsTrigger"]}"
    "dbInstanceIdentifier" = "${var.source_db_instance_identifier}"
    "sourceResourceGroup"  = "${var.source_resource_group}"
    "DATAMASQUE_CONNECTION_ID" = "${var.datamasque_connection_id}"
    "DATAMASQUE_RULESET_ID"  = "${var.datamasque_connection_id}"
    "location"             = azurerm_resource_group.rg.location
  }

  deployment_mode = "Incremental"

  depends_on = [
    azurerm_template_deployment.deploy-logicapp
  ]
}
