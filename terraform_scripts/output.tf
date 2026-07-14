output "resource_group_name" {
  value = azurerm_resource_group.rg.name
}

output "functionapp_name" {
  value = local.functionapp_outputs.functionappName.value
}

output "http_trigger" {
  value     = local.logicapp_outputs.httpsTrigger.value
  sensitive = true
}
