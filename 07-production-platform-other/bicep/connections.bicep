// Foundry connections for an existing Foundry resource and project.
// Order matters: the Key Vault connection is created first, then its role
// assignment, then every other connection depends on both (Foundry does not
// migrate secrets between vaults).
targetScope = 'resourceGroup'

@description('Existing Foundry resource (kind AIServices) with a system-assigned managed identity.')
param foundryName string

@description('Existing Foundry project whose apps and agents reuse the model connection.')
param projectName string

@description('Existing Key Vault in this resource group that stores connection secrets.')
param keyVaultName string

@description('Foundry resource that hosts the shared model deployment. Same subscription only.')
param modelAccountName string

@description('Resource group of the model resource.')
param modelAccountResourceGroup string = resourceGroup().name

@description('Name apps use to find the model endpoint instead of copying endpoint and auth settings.')
param modelConnectionName string = 'shared-model'

resource foundry 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' existing = {
  name: foundryName
}

resource project 'Microsoft.CognitiveServices/accounts/projects@2025-04-01-preview' existing = {
  parent: foundry
  name: projectName
}

resource keyVault 'Microsoft.KeyVault/vaults@2024-11-01' existing = {
  name: keyVaultName
}

resource modelAccount 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' existing = {
  name: modelAccountName
  scope: resourceGroup(modelAccountResourceGroup)
}

// One Key Vault connection per Foundry resource; the resource identity reads and
// writes connection secrets, so no key is stored in the template.
resource keyVaultConnection 'Microsoft.CognitiveServices/accounts/connections@2025-04-01-preview' = {
  parent: foundry
  name: '${foundryName}-keyvault'
  properties: {
    category: 'AzureKeyVault'
    target: keyVault.id
    // Documented auth type for Key Vault connections; the published Bicep type
    // definitions do not list it yet, so Bicep would warn (BCP036).
    #disable-next-line BCP036
    authType: 'AccountManagedIdentity'
    isSharedToAll: true
    metadata: {
      ApiType: 'Azure'
      ResourceId: keyVault.id
      location: keyVault.location
    }
  }
}

// Key Vault Secrets Officer is the least-privileged role the connection supports.
resource keyVaultSecretsOfficer 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, foundry.id, 'Key Vault Secrets Officer')
  scope: keyVault
  properties: {
    principalId: foundry.identity.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'b86a8fe4-44ce-4948-aee5-eccb2c155cd7')
  }
}

// Keyless (Microsoft Entra ID) connection to the model resource, defined once and
// shared by every app and agent in the project. Callers still need a data-plane
// role such as Foundry User on the model resource.
resource modelConnection 'Microsoft.CognitiveServices/accounts/projects/connections@2025-04-01-preview' = {
  parent: project
  name: modelConnectionName
  properties: {
    category: 'AIServices'
    target: modelAccount.properties.endpoint
    authType: 'AAD'
    isSharedToAll: true
    metadata: {
      ApiType: 'Azure'
      ResourceId: modelAccount.id
      location: modelAccount.location
    }
  }
  dependsOn: [
    keyVaultConnection
    keyVaultSecretsOfficer
  ]
}

output keyVaultConnectionName string = keyVaultConnection.name
output modelConnectionName string = modelConnection.name
