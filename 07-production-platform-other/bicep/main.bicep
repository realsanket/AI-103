targetScope = 'resourceGroup'

@description('Region for this independently deployable production cell.')
param location string = resourceGroup().location

@description('Unique, lowercase production-cell prefix. Keep it under 24 characters.')
@minLength(3)
@maxLength(24)
param prefix string

@description('Foundry project name. This template never creates a model deployment.')
param projectName string = 'production'

@description('CIDR for the production-cell virtual network.')
param vnetAddressPrefix string = '10.42.0.0/16'

@description('CIDR for private endpoints.')
param privateEndpointSubnetPrefix string = '10.42.1.0/24'

@description('CIDR for Foundry Agent Service VNet injection. /27 is the supported minimum.')
param agentSubnetPrefix string = '10.42.2.0/24'

var suffix = toLower(uniqueString(subscription().id, resourceGroup().id, prefix, location))
var foundryName = toLower('${prefix}-fd-${take(suffix, 8)}')
var keyVaultName = toLower('${prefix}kv${take(suffix, 8)}')
var storageName = toLower('${replace(prefix, '-', '')}${take(suffix, 12)}')
var workspaceName = '${prefix}-law-${take(suffix, 8)}'
var vnetName = '${prefix}-vnet'
var identityName = '${prefix}-foundry-uai'

resource vnet 'Microsoft.Network/virtualNetworks@2024-05-01' = {
  name: vnetName
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        vnetAddressPrefix
      ]
    }
    subnets: [
      {
        name: 'private-endpoints'
        properties: {
          addressPrefix: privateEndpointSubnetPrefix
          privateEndpointNetworkPolicies: 'Disabled'
        }
      }
      {
        name: 'agent-injection'
        properties: {
          addressPrefix: agentSubnetPrefix
          delegations: [
            {
              name: 'foundry-agent-service'
              properties: {
                serviceName: 'Microsoft.App/environments'
              }
            }
          ]
        }
      }
    ]
  }
}

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    enableRbacAuthorization: true
    enablePurgeProtection: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    publicNetworkAccess: 'Disabled'
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Deny'
    }
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
  }
}

resource key 'Microsoft.KeyVault/vaults/keys@2023-07-01' = {
  parent: keyVault
  name: 'foundry-cmk'
  properties: {
    kty: 'RSA'
    keySize: 2048
    attributes: {
      enabled: true
    }
  }
}

resource keyVaultCryptoUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, identity.id, 'Key Vault Crypto User')
  scope: keyVault
  properties: {
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '12338af0-0e69-4776-bea7-57ae8d297424')
  }
}

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageName
  location: location
  sku: {
    name: 'Standard_GZRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    minimumTlsVersion: 'TLS1_2'
    publicNetworkAccess: 'Disabled'
  }
}

resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: workspaceName
  location: location
  properties: {
    retentionInDays: 90
    sku: {
      name: 'PerGB2018'
    }
  }
}

resource foundry 'Microsoft.CognitiveServices/accounts@2026-03-01' = {
  name: foundryName
  location: location
  kind: 'AIServices'
  sku: {
    name: 'S0'
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${identity.id}': {}
    }
  }
  properties: {
    allowProjectManagement: true
    customSubDomainName: foundryName
    disableLocalAuth: true
    publicNetworkAccess: 'Disabled'
    networkAcls: {
      defaultAction: 'Deny'
    }
    networkInjections: [
      {
        scenario: 'agent'
        subnetArmId: '${vnet.id}/subnets/agent-injection'
        useMicrosoftManagedNetwork: false
      }
    ]
    encryption: {
      keySource: 'Microsoft.KeyVault'
      keyVaultProperties: {
        keyName: key.name
        keyVersion: key.properties.keyUriWithVersion
        keyVaultUri: keyVault.properties.vaultUri
      }
    }
  }
}

resource project 'Microsoft.CognitiveServices/accounts/projects@2026-03-01' = {
  parent: foundry
  name: projectName
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${identity.id}': {}
    }
  }
  properties: {
    displayName: projectName
  }
}

resource foundryDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  scope: foundry
  name: 'to-log-analytics'
  properties: {
    workspaceId: workspace.id
    logs: [
      {
        category: 'Audit'
        enabled: true
      }
      {
        category: 'RequestResponse'
        enabled: true
      }
      {
        category: 'AzureOpenAIRequestUsage'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
      }
    ]
  }
}

resource privateZones 'Microsoft.Network/privateDnsZones@2024-06-01' = [for zone in [
  'privatelink.cognitiveservices.azure.com'
  'privatelink.openai.azure.com'
  'privatelink.services.ai.azure.com'
  'privatelink.vaultcore.azure.net'
  'privatelink.blob.${environment().suffixes.storage}'
]: {
  name: zone
  location: 'global'
}]

resource privateZoneLinks 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = [for (zone, index) in [
  'privatelink.cognitiveservices.azure.com'
  'privatelink.openai.azure.com'
  'privatelink.services.ai.azure.com'
  'privatelink.vaultcore.azure.net'
  'privatelink.blob.${environment().suffixes.storage}'
]: {
  parent: privateZones[index]
  name: '${vnetName}-link'
  location: 'global'
  properties: {
    registrationEnabled: false
    virtualNetwork: {
      id: vnet.id
    }
  }
}]

resource foundryPrivateEndpoint 'Microsoft.Network/privateEndpoints@2024-05-01' = {
  name: '${foundryName}-pe'
  location: location
  properties: {
    subnet: {
      id: '${vnet.id}/subnets/private-endpoints'
    }
    privateLinkServiceConnections: [
      {
        name: '${foundryName}-connection'
        properties: {
          groupIds: [
            'account'
          ]
          privateLinkServiceId: foundry.id
        }
      }
    ]
  }
}

resource foundryPrivateDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-05-01' = {
  parent: foundryPrivateEndpoint
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [for index in range(0, 3): {
      name: 'foundry-${index}'
      properties: {
        privateDnsZoneId: privateZones[index].id
      }
    }]
  }
}

resource keyVaultPrivateEndpoint 'Microsoft.Network/privateEndpoints@2024-05-01' = {
  name: '${keyVaultName}-pe'
  location: location
  properties: {
    subnet: {
      id: '${vnet.id}/subnets/private-endpoints'
    }
    privateLinkServiceConnections: [
      {
        name: '${keyVaultName}-connection'
        properties: {
          groupIds: [
            'vault'
          ]
          privateLinkServiceId: keyVault.id
        }
      }
    ]
  }
}

resource keyVaultPrivateDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-05-01' = {
  parent: keyVaultPrivateEndpoint
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'key-vault'
        properties: {
          privateDnsZoneId: privateZones[3].id
        }
      }
    ]
  }
}

resource storagePrivateEndpoint 'Microsoft.Network/privateEndpoints@2024-05-01' = {
  name: '${storageName}-blob-pe'
  location: location
  properties: {
    subnet: {
      id: '${vnet.id}/subnets/private-endpoints'
    }
    privateLinkServiceConnections: [
      {
        name: '${storageName}-blob-connection'
        properties: {
          groupIds: [
            'blob'
          ]
          privateLinkServiceId: storage.id
        }
      }
    ]
  }
}

resource storagePrivateDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-05-01' = {
  parent: storagePrivateEndpoint
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'blob'
        properties: {
          privateDnsZoneId: privateZones[4].id
        }
      }
    ]
  }
}

resource foundryDeleteLock 'Microsoft.Authorization/locks@2020-05-01' = {
  name: '${foundry.name}-can-not-delete'
  scope: foundry
  properties: {
    level: 'CanNotDelete'
    notes: 'Production baseline: remove only through approved change control.'
  }
}

resource keyVaultDeleteLock 'Microsoft.Authorization/locks@2020-05-01' = {
  name: '${keyVault.name}-can-not-delete'
  scope: keyVault
  properties: {
    level: 'CanNotDelete'
    notes: 'Production baseline: remove only through approved change control.'
  }
}

resource storageDeleteLock 'Microsoft.Authorization/locks@2020-05-01' = {
  name: '${storage.name}-can-not-delete'
  scope: storage
  properties: {
    level: 'CanNotDelete'
    notes: 'Production baseline: remove only through approved change control.'
  }
}

output foundryResourceId string = foundry.id
output projectEndpoint string = 'https://${foundryName}.services.ai.azure.com/api/projects/${projectName}'
output privateEndpointSubnetId string = '${vnet.id}/subnets/private-endpoints'
output agentInjectionSubnetId string = '${vnet.id}/subnets/agent-injection'
