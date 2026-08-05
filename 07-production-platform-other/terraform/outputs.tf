output "foundry_resource_id" {
  value = azapi_resource.foundry.id
}

output "project_endpoint" {
  value = "https://${var.foundry_name}.services.ai.azure.com/api/projects/${var.project_name}"
}

output "agent_injection_subnet_id" {
  value = azurerm_subnet.agent_injection.id
}

output "log_analytics_workspace_id" {
  value = azurerm_log_analytics_workspace.platform.id
}
