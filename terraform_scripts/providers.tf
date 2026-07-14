terraform {

  required_version = ">=1.3"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.116"
    }
    random = {
      source  = "hashicorp/random"
      version = "~>3.6"
    }
    null = {
      source  = "hashicorp/null"
      version = "~>3.2"
    }
  }
}

# terraform {
#   cloud {
#     organization = ""

#     workspaces {
#       name = ""
#     }
#   }
# }

provider "azurerm" {
  features {}

  subscription_id = var.subscription_id
  tenant_id       = var.tenant
  client_id       = var.appId
  client_secret   = var.password
}