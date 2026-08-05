targetScope = 'subscription'

@description('Resource group that receives the policy assignment.')
param resourceGroupName string

@description('Foundry connection categories approved by platform governance.')
param allowedCategories array

resource definition 'Microsoft.Authorization/policyDefinitions@2023-04-01' = {
  name: 'deny-unapproved-foundry-connections'
  properties: {
    displayName: 'Deny unapproved Foundry connection categories'
    description: 'Allows only platform-approved Microsoft Foundry connection categories.'
    mode: 'All'
    parameters: loadJsonContent('../policy/deny-unapproved-foundry-connections.json', '$.parameters')
    policyRule: loadJsonContent('../policy/deny-unapproved-foundry-connections.json', '$.policyRule')
  }
}

module assignment 'policy-assignment.bicep' = {
  name: 'approved-foundry-connections'
  scope: resourceGroup(resourceGroupName)
  params: {
    allowedCategories: allowedCategories
    policyDefinitionId: definition.id
  }
}
