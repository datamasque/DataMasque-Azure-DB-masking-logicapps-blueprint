variable "prefix" {
  type        = string
  description = "Terraform uses shortened names without the common prefix to interact with workspaces."
}
variable "subscription_id" {
  type        = string
  description = "The subscription id is obtained from Azure Login. Subscription id where you want to add resource."
}

variable "tenant" {
  type        = string
  description = "The tenant is obtained from the service principal creation step."
}

variable "database_id" {
  type        = string
  description = "The database_id Azure SQL server."
}


variable "appId" {
  type        = string
  description = "The app is obtained from the service principal creation step."
}

variable "password" {
  type        = string
  description = "The password is obtained from the service principal creation step."
}

variable "resource_group_location" {
  type        = string
  description = "The location is value azure region where the new resource group should exist"
}

variable "datamasque_base_url" {
  type        = string
  description = "DATAMASQUE instance URL"
}

variable "datamasque_connection_id" {
  type        = string
  description = "DATAMASQUE connection ID"
}

variable "datamasque_ruleset_id" {
  type        = string
  description = "DATAMASQUE Rule Set ID"
}

variable "keyvault_resource_group" {
  type        = string
  description = "The resource group name contains Azure KeyVault."
}

variable "datamasque_keyvault" {
  type        = string
  description = "Azure Key Vault name"
}

variable "secret_name" {
  type        = string
  description = "Key Vault secret for DATAMASQUE instance credentials and SQL server."
}

variable "container_name" {
  type        = string
  default     = "masked-database"
  description = "File storage location is masked after exporting."
}

variable "storage_accounts_name_prefix" {
  type        = string
  default     = "storage"
  description = "Prefix of the storage account name that's combined with a random ID so name is unique in your Azure subscription."
}

variable "serverfarms_name_prefix" {
  type        = string
  default     = "asp"
  description = "Prefix of the server farms name that's combined with a random ID so name is unique in your Azure subscription."
}

variable "function_app_name_prefix" {
  type        = string
  default     = "function"
  description = "Prefix of the function app name that's combined with a random ID so name is unique in your Azure subscription."
}

variable "manual_trigger_name_prefix" {
  type        = string
  default     = "logic"
  description = "Prefix of the manual trigger name that's combined with a random ID so name is unique in your Azure subscription."
}

variable "recurring_trigger_name_prefix" {
  type        = string
  default     = "logic-recurring"
  description = "Prefix of the recurring trigger name that's combined with a random ID so name is unique in your Azure subscription."
}

variable "source_db_instance_identifier" {
  type        = string
  default     = "demo222"
  description = "The source Azure SQL server."
}

variable "source_resource_group" {
  type        = string
  default     = "datamasque"
  description = "The source resource group contains Azure SQL server"
}

variable "interval_time" {
  type        = number
  default     = 120
  description = "Poll interval in seconds for the Logic App wait loops."
}

variable "max_wait_iterations" {
  type        = number
  default     = 720
  description = "Maximum poll iterations per wait loop before it gives up (decoupled from interval_time). The PT1H per-loop timeout is the real ceiling; raise both for masking runs expected to exceed an hour."
}

variable "allow_azure_services" {
  type        = bool
  default     = false
  description = "Add the Azure SQL 'Allow Azure services' (0.0.0.0) firewall rule to the staging server. Leave false unless the DataMasque instance reaches staging as an Azure service without a static IP inherited from the source server's rules."
}

variable "datamasque_verify_tls" {
  type        = bool
  default     = true
  description = "Verify the DataMasque instance's TLS certificate. Set false only for a trusted self-signed/private instance."
}

variable "run_secret" {
  type        = string
  default     = ""
  sensitive   = true
  description = "DataMasque run secret. Source from configuration/secret store; never commit a literal."
}