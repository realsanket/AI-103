terraform {
  required_version = ">= 1.9.0"

  required_providers {
    azapi = {
      source  = "Azure/azapi"
      version = "~> 2.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
}

provider "azapi" {}

data "azurerm_client_config" "current" {}

locals {
  dns_zones = toset([
    "privatelink.cognitiveservices.azure.com",
    "privatelink.openai.azure.com",
    "privatelink.services.ai.azure.com",
    "privatelink.vaultcore.azure.net",
    "privatelink.blob.core.windows.net",
  ])
}

resource "azurerm_resource_group" "platform" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

resource "azurerm_user_assigned_identity" "foundry" {
  name                = "${var.prefix}-foundry-uai"
  resource_group_name = azurerm_resource_group.platform.name
  location            = azurerm_resource_group.platform.location
  tags                = var.tags
}

resource "azurerm_virtual_network" "platform" {
  name                = "${var.prefix}-vnet"
  resource_group_name = azurerm_resource_group.platform.name
  location            = azurerm_resource_group.platform.location
  address_space       = [var.vnet_address_space]
  tags                = var.tags
}

resource "azurerm_subnet" "private_endpoints" {
  name                              = "private-endpoints"
  resource_group_name               = azurerm_resource_group.platform.name
  virtual_network_name              = azurerm_virtual_network.platform.name
  address_prefixes                  = [var.private_endpoint_subnet_prefix]
  private_endpoint_network_policies = "Disabled"
}

resource "azurerm_subnet" "agent_injection" {
  name                 = "agent-injection"
  resource_group_name  = azurerm_resource_group.platform.name
  virtual_network_name = azurerm_virtual_network.platform.name
  address_prefixes     = [var.agent_subnet_prefix]

  delegation {
    name = "foundry-agent-service"
    service_delegation {
      name = "Microsoft.App/environments"
    }
  }
}

resource "azurerm_private_dns_zone" "platform" {
  for_each            = local.dns_zones
  name                = each.value
  resource_group_name = azurerm_resource_group.platform.name
}

resource "azurerm_private_dns_zone_virtual_network_link" "platform" {
  for_each              = azurerm_private_dns_zone.platform
  name                  = "${var.prefix}-vnet-link"
  resource_group_name   = azurerm_resource_group.platform.name
  private_dns_zone_name = each.value.name
  virtual_network_id    = azurerm_virtual_network.platform.id
  registration_enabled  = false
}

resource "azurerm_key_vault" "platform" {
  name                          = var.key_vault_name
  resource_group_name           = azurerm_resource_group.platform.name
  location                      = azurerm_resource_group.platform.location
  tenant_id                     = data.azurerm_client_config.current.tenant_id
  sku_name                      = "standard"
  rbac_authorization_enabled    = true
  purge_protection_enabled      = true
  soft_delete_retention_days    = 90
  public_network_access_enabled = false
  tags                          = var.tags

  network_acls {
    bypass         = "AzureServices"
    default_action = "Deny"
  }
}

# Created through ARM (control plane), like the Bicep baseline. The vault has no
# public data-plane access, so a data-plane key resource would fail from a runner
# outside the VNet. ARM cannot delete Key Vault keys: tear down by deleting the
# resource group after removing the locks.
resource "azapi_resource" "foundry_cmk" {
  type      = "Microsoft.KeyVault/vaults/keys@2023-07-01"
  name      = "foundry-cmk"
  parent_id = azurerm_key_vault.platform.id

  body = {
    properties = {
      kty     = "RSA"
      keySize = 2048
      keyOps  = ["wrapKey", "unwrapKey"]
      attributes = {
        enabled = true
      }
    }
  }
}

resource "azurerm_role_assignment" "foundry_cmk" {
  scope                = azurerm_key_vault.platform.id
  role_definition_name = "Key Vault Crypto User"
  principal_id         = azurerm_user_assigned_identity.foundry.principal_id
}

resource "azurerm_storage_account" "platform" {
  name                              = var.storage_account_name
  resource_group_name               = azurerm_resource_group.platform.name
  location                          = azurerm_resource_group.platform.location
  account_tier                      = "Standard"
  account_replication_type          = "GZRS"
  min_tls_version                   = "TLS1_2"
  public_network_access_enabled     = false
  allow_nested_items_to_be_public   = false
  shared_access_key_enabled         = false
  infrastructure_encryption_enabled = true
  tags                              = var.tags
}

resource "azurerm_log_analytics_workspace" "platform" {
  name                = "${var.prefix}-law"
  resource_group_name = azurerm_resource_group.platform.name
  location            = azurerm_resource_group.platform.location
  sku                 = "PerGB2018"
  retention_in_days   = 90
  tags                = var.tags
}

resource "azapi_resource" "foundry" {
  type      = "Microsoft.CognitiveServices/accounts@2026-03-01"
  name      = var.foundry_name
  parent_id = azurerm_resource_group.platform.id
  location  = azurerm_resource_group.platform.location

  body = {
    kind = "AIServices"
    sku = {
      name = "S0"
    }
    identity = {
      type = "UserAssigned"
      userAssignedIdentities = {
        (azurerm_user_assigned_identity.foundry.id) = {}
      }
    }
    properties = {
      allowProjectManagement = true
      customSubDomainName    = var.foundry_name
      disableLocalAuth       = true
      publicNetworkAccess    = "Disabled"
      networkAcls = {
        defaultAction = "Deny"
      }
      networkInjections = [
        {
          scenario                   = "agent"
          subnetArmId                = azurerm_subnet.agent_injection.id
          useMicrosoftManagedNetwork = false
        },
      ]
      encryption = {
        keySource = "Microsoft.KeyVault"
        # keyVersion is omitted so the account follows key rotation automatically.
        # identityClientId selects the user-assigned identity that unwraps the key.
        keyVaultProperties = {
          keyName          = azapi_resource.foundry_cmk.name
          keyVaultUri      = azurerm_key_vault.platform.vault_uri
          identityClientId = azurerm_user_assigned_identity.foundry.client_id
        }
      }
    }
    tags = var.tags
  }

  depends_on = [azurerm_role_assignment.foundry_cmk]
}

resource "azapi_resource" "project" {
  type      = "Microsoft.CognitiveServices/accounts/projects@2026-03-01"
  name      = var.project_name
  parent_id = azapi_resource.foundry.id
  location  = azurerm_resource_group.platform.location

  body = {
    identity = {
      type = "UserAssigned"
      userAssignedIdentities = {
        (azurerm_user_assigned_identity.foundry.id) = {}
      }
    }
    properties = {
      displayName = var.project_name
    }
  }
}

resource "azurerm_private_endpoint" "foundry" {
  name                = "${var.foundry_name}-pe"
  resource_group_name = azurerm_resource_group.platform.name
  location            = azurerm_resource_group.platform.location
  subnet_id           = azurerm_subnet.private_endpoints.id
  tags                = var.tags

  private_service_connection {
    name                           = "${var.foundry_name}-connection"
    private_connection_resource_id = azapi_resource.foundry.id
    subresource_names              = ["account"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name = "default"
    private_dns_zone_ids = [
      azurerm_private_dns_zone.platform["privatelink.cognitiveservices.azure.com"].id,
      azurerm_private_dns_zone.platform["privatelink.openai.azure.com"].id,
      azurerm_private_dns_zone.platform["privatelink.services.ai.azure.com"].id,
    ]
  }
}

resource "azurerm_private_endpoint" "key_vault" {
  name                = "${var.key_vault_name}-pe"
  resource_group_name = azurerm_resource_group.platform.name
  location            = azurerm_resource_group.platform.location
  subnet_id           = azurerm_subnet.private_endpoints.id
  tags                = var.tags

  private_service_connection {
    name                           = "${var.key_vault_name}-connection"
    private_connection_resource_id = azurerm_key_vault.platform.id
    subresource_names              = ["vault"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "default"
    private_dns_zone_ids = [azurerm_private_dns_zone.platform["privatelink.vaultcore.azure.net"].id]
  }
}

resource "azurerm_private_endpoint" "storage" {
  name                = "${var.storage_account_name}-blob-pe"
  resource_group_name = azurerm_resource_group.platform.name
  location            = azurerm_resource_group.platform.location
  subnet_id           = azurerm_subnet.private_endpoints.id
  tags                = var.tags

  private_service_connection {
    name                           = "${var.storage_account_name}-blob-connection"
    private_connection_resource_id = azurerm_storage_account.platform.id
    subresource_names              = ["blob"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "default"
    private_dns_zone_ids = [azurerm_private_dns_zone.platform["privatelink.blob.core.windows.net"].id]
  }
}

resource "azapi_resource" "foundry_diagnostics" {
  type      = "Microsoft.Insights/diagnosticSettings@2021-05-01-preview"
  name      = "to-log-analytics"
  parent_id = azapi_resource.foundry.id
  body = {
    properties = {
      workspaceId = azurerm_log_analytics_workspace.platform.id
      logs = [
        { category = "Audit", enabled = true },
        { category = "RequestResponse", enabled = true },
        { category = "AzureOpenAIRequestUsage", enabled = true },
      ]
      metrics = [
        { category = "AllMetrics", enabled = true },
      ]
    }
  }
}

resource "azurerm_management_lock" "foundry" {
  name       = "${var.foundry_name}-can-not-delete"
  scope      = azapi_resource.foundry.id
  lock_level = "CanNotDelete"
  notes      = "Production baseline: remove only through approved change control."
}

resource "azurerm_management_lock" "key_vault" {
  name       = "${var.key_vault_name}-can-not-delete"
  scope      = azurerm_key_vault.platform.id
  lock_level = "CanNotDelete"
  notes      = "Production baseline: remove only through approved change control."
}

resource "azurerm_management_lock" "storage" {
  name       = "${var.storage_account_name}-can-not-delete"
  scope      = azurerm_storage_account.platform.id
  lock_level = "CanNotDelete"
  notes      = "Production baseline: remove only through approved change control."
}

resource "azurerm_policy_definition" "approved_foundry_connections" {
  name         = "deny-unapproved-foundry-connections"
  policy_type  = "Custom"
  mode         = "All"
  display_name = "Deny unapproved Foundry connection categories"
  description  = "Allows only platform-approved Microsoft Foundry connection categories."
  policy_rule  = jsonencode(jsondecode(file("${path.module}/../policy/deny-unapproved-foundry-connections.json")).policyRule)
  parameters   = jsonencode(jsondecode(file("${path.module}/../policy/deny-unapproved-foundry-connections.json")).parameters)
}

resource "azurerm_resource_group_policy_assignment" "approved_foundry_connections" {
  count                = var.assign_connection_policy ? 1 : 0
  name                 = "approved-foundry-connections"
  resource_group_id    = azurerm_resource_group.platform.id
  policy_definition_id = azurerm_policy_definition.approved_foundry_connections.id
  parameters = jsonencode({
    allowedCategories = {
      value = var.allowed_connection_categories
    }
  })
}
