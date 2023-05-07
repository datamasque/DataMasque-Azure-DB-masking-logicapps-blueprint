output "resource_group_name" {
  value = "${azurerm_resource_group.rg.name}"
}

output "functionapp_name" {
  value = "${azurerm_template_deployment.deploy-functionapp.outputs["functionappName"]}"
}

output "http_trigger" {
  value = "${azurerm_template_deployment.deploy-logicapp.outputs["httpsTrigger"]}"
}