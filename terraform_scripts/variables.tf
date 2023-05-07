variable "prefix" {
  description = "Terraform uses shortened names without the common prefix to interact with workspaces."
}
variable "subscription_id" {
  description = "The subscription id is obtained from Azure Login. Subscription id where you want to add resource."
}

variable "tenant" {
  description = "The tenant is obtained from the service principal creation step."
}

variable "database_id" {
  description = "The database_id Azure SQL server."
}


variable "appId" {
  description = "The app is obtained from the service principal creation step."
}

variable "password" {
  description = "The password is obtained from the service principal creation step."
}

variable "resource_group_location" {
  description = "The location is value azure region where the new resource group should exist"
}

variable "datamasque_base_url" {
  description = "DATAMASQUE instance URL"
}

variable "datamasque_connection_id" {
  description = "DATAMASQUE connection ID"
}

variable "datamasque_ruleset_id" {
  description = "DATAMASQUE Rule Set ID"
}

variable "keyvault_resource_group" {
  description = "The resource group name contains Azure KeyVault."
}

variable "datamasque_keyvault" {
  description = "Azure Key Vault name"
}

variable "secret_name" {
  description = "Key Vault secret for DATAMASQUE instance credentials and SQL server."
}

variable "container_name" {
  default = "masked-database"
  description = "File storage location is masked after exporting."
}

variable "storage_accounts_name_prefix" {
  default = "storage"
  description = "Prefix of the storage account name that's combined with a random ID so name is unique in your Azure subscription."
}

variable "serverfarms_name_prefix" {
  default = "asp"
  description = "Prefix of the server farms name that's combined with a random ID so name is unique in your Azure subscription."
}

variable "function_app_name_prefix" {
  default = "function"
  description = "Prefix of the function app name that's combined with a random ID so name is unique in your Azure subscription."
}

variable "manual_trigger_name_prefix" {
  default = "logic"
  description = "Prefix of the manual trigger name that's combined with a random ID so name is unique in your Azure subscription."
}

variable "recurring_trigger_name_prefix" {
  default = "logic-recurring"
  description = "Prefix of the recurring trigger name that's combined with a random ID so name is unique in your Azure subscription."
}

variable "source_db_instance_identifier" {
  default = "demo222"
  description = "The source Azure SQL server."
}

variable "source_resource_group" {
  default = "datamasque"
  description = "The source resource group contains Azure SQL server"
}

variable "interval_time" {
  type = number
  default = 120
  description = "The interval time (seconds)."
}