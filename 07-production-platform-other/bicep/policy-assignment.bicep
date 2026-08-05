targetScope = 'resourceGroup'

param policyDefinitionId string
param allowedCategories array

resource assignment 'Microsoft.Authorization/policyAssignments@2024-04-01' = {
  name: 'approved-foundry-connections'
  properties: {
    displayName: 'Approved Foundry connection categories'
    policyDefinitionId: policyDefinitionId
    parameters: {
      allowedCategories: {
        value: allowedCategories
      }
    }
  }
}
