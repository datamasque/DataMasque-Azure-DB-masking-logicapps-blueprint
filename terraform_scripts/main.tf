locals {
  # Decoded ARM deployment outputs (azurerm_resource_group_template_deployment
  # returns a JSON string in output_content).
  storage_outputs     = jsondecode(azurerm_resource_group_template_deployment.deploy-storage.output_content)
  serverfarms_outputs = jsondecode(azurerm_resource_group_template_deployment.deploy-serverfarms.output_content)
  functionapp_outputs = jsondecode(azurerm_resource_group_template_deployment.deploy-functionapp.output_content)
  logicapp_outputs    = jsondecode(azurerm_resource_group_template_deployment.deploy-logicapp.output_content)
}

resource "random_id" "rng" {
  keepers = {
    first = timestamp()
  }
  byte_length = 8
}

resource "azurerm_resource_group" "rg" {
  name     = "${var.prefix}rg-${random_id.rng.hex}"
  location = var.resource_group_location
}

resource "azurerm_resource_group_template_deployment" "deploy-storage" {
  name                = "deploy-storage-${random_id.rng.hex}"
  resource_group_name = azurerm_resource_group.rg.name
  deployment_mode     = "Incremental"

  template_content = file("arm_templates/storage_accounts.json")

  parameters_content = jsonencode({
    "storageAccountsNamePrefix" = { value = "${var.prefix}${var.storage_accounts_name_prefix}" }
    "containerName"             = { value = var.container_name }
    "location"                  = { value = azurerm_resource_group.rg.location }
  })
}

resource "azurerm_resource_group_template_deployment" "deploy-serverfarms" {
  name                = "deploy-serverfarms-${random_id.rng.hex}"
  resource_group_name = azurerm_resource_group.rg.name
  deployment_mode     = "Incremental"

  template_content = file("arm_templates/server_farms.json")

  parameters_content = jsonencode({
    "serverfarmsNamePrefix" = { value = "${var.prefix}-${var.serverfarms_name_prefix}" }
    "location"              = { value = azurerm_resource_group.rg.location }
  })
}

resource "azurerm_resource_group_template_deployment" "deploy-functionapp" {
  name                = "deploy-functionapp-${random_id.rng.hex}"
  resource_group_name = azurerm_resource_group.rg.name
  deployment_mode     = "Incremental"

  template_content = file("arm_templates/functionapp.json")

  parameters_content = jsonencode({
    "functionAppNamePrefix"   = { value = "${var.prefix}-${var.function_app_name_prefix}" }
    "location"                = { value = azurerm_resource_group.rg.location }
    "serverfarmsExternalID"   = { value = local.serverfarms_outputs.serverfarmsExternalID.value }
    "storageAccountName"      = { value = local.storage_outputs.storageAccountName.value }
    "storageBlobUri"          = { value = local.storage_outputs.storageBlobUri.value }
    "storageAccountAccessKey" = { value = local.storage_outputs.storageAccountAccessKey.value }
    "subscriptionID"          = { value = var.subscription_id }
    "tenantID"                = { value = var.tenant }
    "clientID"                = { value = var.appId }
    "clientSecret"            = { value = var.password }
    "datamasqueBaseUrl"       = { value = var.datamasque_base_url }
    "datamasqueKeyVault"      = { value = var.datamasque_keyvault }
    "secretName"              = { value = var.secret_name }
    "keyvaultResourceGroup"   = { value = var.keyvault_resource_group }
    "databaseID"              = { value = var.database_id }
    "datamasqueVerifyTls"     = { value = tostring(var.datamasque_verify_tls) }
    "runSecret"               = { value = var.run_secret }
    "allowAzureServices"      = { value = tostring(var.allow_azure_services) }
  })

  depends_on = [
    azurerm_resource_group_template_deployment.deploy-storage,
    azurerm_resource_group_template_deployment.deploy-serverfarms
  ]
}

resource "null_resource" "publish-functionapp" {
  triggers = {
    functions = random_id.rng.hex
  }

  # `func azure functionapp publish` retries until the app is reachable, so the
  # publish depends directly on the deployment rather than a fixed 30s sleep.
  provisioner "local-exec" {
    command = "cd ../functions && func azure functionapp publish ${local.functionapp_outputs.functionappName.value}"
  }

  depends_on = [
    azurerm_resource_group_template_deployment.deploy-functionapp
  ]
}

resource "azurerm_key_vault_access_policy" "key-vault-policy" {
  key_vault_id = local.functionapp_outputs.keyVaultID.value
  tenant_id    = var.tenant
  object_id    = local.functionapp_outputs.principalID.value

  secret_permissions = [
    "Get",
    "List"
  ]

  depends_on = [null_resource.publish-functionapp]
}

resource "azurerm_resource_group_template_deployment" "deploy-logicapp" {
  name                = "deploy-logicapp-${random_id.rng.hex}"
  resource_group_name = azurerm_resource_group.rg.name
  deployment_mode     = "Incremental"

  template_content = file("arm_templates/logic_app_manually_trigger.json")

  parameters_content = jsonencode({
    "workflowsNamePrefix"      = { value = "${var.prefix}-${var.manual_trigger_name_prefix}" }
    "functionAppName"          = { value = local.functionapp_outputs.functionappName.value }
    "dbInstanceIdentifier"     = { value = var.source_db_instance_identifier }
    "sourceResourceGroup"      = { value = var.source_resource_group }
    "DATAMASQUE_CONNECTION_ID" = { value = var.datamasque_connection_id }
    "DATAMASQUE_RULESET_ID"    = { value = var.datamasque_ruleset_id }
    "intervalTime"             = { value = var.interval_time }
    "maxWaitIterations"        = { value = var.max_wait_iterations }
    "location"                 = { value = azurerm_resource_group.rg.location }
  })

  depends_on = [null_resource.publish-functionapp]
}

resource "azurerm_resource_group_template_deployment" "deploy-logicapp-recurring" {
  name                = "deploy-logicapp-recurring-${random_id.rng.hex}"
  resource_group_name = azurerm_resource_group.rg.name
  deployment_mode     = "Incremental"

  template_content = file("arm_templates/logic_app_recurring_trigger.json")

  parameters_content = jsonencode({
    "workflowsNamePrefix"      = { value = "${var.prefix}-${var.recurring_trigger_name_prefix}" }
    "httpTrigger"              = { value = local.logicapp_outputs.httpsTrigger.value }
    "dbInstanceIdentifier"     = { value = var.source_db_instance_identifier }
    "sourceResourceGroup"      = { value = var.source_resource_group }
    "DATAMASQUE_CONNECTION_ID" = { value = var.datamasque_connection_id }
    "DATAMASQUE_RULESET_ID"    = { value = var.datamasque_ruleset_id }
    "location"                 = { value = azurerm_resource_group.rg.location }
  })

  depends_on = [
    azurerm_resource_group_template_deployment.deploy-logicapp
  ]
}
