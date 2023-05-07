terraform {

  required_version = ">=0.12"
  
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
      version = "~>2.0"
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

  subscription_id   = "${var.subscription_id}"
  tenant_id         = "${var.tenant}"
  client_id         = "${var.appId}"
  client_secret     = "${var.password}"
}