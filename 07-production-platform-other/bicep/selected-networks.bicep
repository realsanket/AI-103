// Restrict a Foundry Tools resource (Language, Speech, and other services) to
// selected subnets on its public endpoint: virtual network rules plus a
// Microsoft.CognitiveServices service endpoint on each allowed subnet.
// Lesson 01 shows the stricter alternative: a private endpoint with public
// network access disabled.
targetScope = 'resourceGroup'

@description('Region for the resource and its virtual network.')
param location string = resourceGroup().location

@description('Unique, lowercase prefix. Keep it under 24 characters.')
@minLength(3)
@maxLength(24)
param prefix string

@description('CIDR for the virtual network.')
param vnetAddressPrefix string = '10.43.0.0/16'

@description('CIDR for the application subnet that is allowed to call the resource.')
param appSubnetPrefix string = '10.43.1.0/24'

var accountName = toLower('${prefix}-tools-${take(uniqueString(resourceGroup().id, prefix), 6)}')

resource vnet 'Microsoft.Network/virtualNetworks@2024-05-01' = {
  name: '${prefix}-apps-vnet'
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        vnetAddressPrefix
      ]
    }
    subnets: [
      {
        name: 'apps'
        properties: {
          addressPrefix: appSubnetPrefix
          // The service endpoint sends the subnet identity with each request.
          serviceEndpoints: [
            {
              service: 'Microsoft.CognitiveServices'
            }
          ]
        }
      }
    ]
  }
}

resource account 'Microsoft.CognitiveServices/accounts@2026-03-01' = {
  name: accountName
  location: location
  kind: 'AIServices'
  sku: {
    name: 'S0'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    // Network rules only apply to calls made to the custom subdomain endpoint.
    customSubDomainName: accountName
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      // Deny is required; without it the rules below have no effect.
      defaultAction: 'Deny'
      ipRules: []
      virtualNetworkRules: [
        {
          id: '${vnet.id}/subnets/apps'
          ignoreMissingVnetServiceEndpoint: false
        }
      ]
    }
  }
}

output accountEndpoint string = account.properties.endpoint
output allowedSubnetId string = '${vnet.id}/subnets/apps'
