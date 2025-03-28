@description('The location for all resources')
param location string = resourceGroup().location

@description('Environment name (dev, staging, prod)')
param environmentName string

@description('Project name')
param projectName string = 'azureshield'

@description('Tags for all resources')
param tags object = {
  Environment: environmentName
  Project: projectName
  ManagedBy: 'bicep'
}

// Resource names
var acrName = '${projectName}${environmentName}acr'
var aksName = '${projectName}${environmentName}aks'
var postgresName = '${projectName}${environmentName}psql'
var redisName = '${projectName}${environmentName}redis'
var keyVaultName = '${projectName}${environmentName}kv'
var appInsightsName = '${projectName}${environmentName}ai'
var logAnalyticsName = '${projectName}${environmentName}logs'
var vnetName = '${projectName}${environmentName}vnet'
var subnetName = '${projectName}${environmentName}subnet'

// Network configuration
var addressPrefix = '10.0.0.0/16'
var subnetPrefix = '10.0.1.0/24'

// Resource SKUs
var postgresSku = environmentName == 'prod' ? 'GP_Gen5_2' : 'B_Gen5_1'
var redisSku = environmentName == 'prod' ? 'Standard' : 'Basic'
var aksNodeCount = environmentName == 'prod' ? 3 : 1

// Create Virtual Network
resource vnet 'Microsoft.Network/virtualNetworks@2023-05-01' = {
  name: vnetName
  location: location
  tags: tags
  properties: {
    addressSpace: {
      addressPrefixes: [
        addressPrefix
      ]
    }
    subnets: [
      {
        name: subnetName
        properties: {
          addressPrefix: subnetPrefix
          delegations: [
            {
              name: 'aks-delegation'
              properties: {
                serviceName: 'Microsoft.ContainerService/managedClusters'
              }
            }
          ]
        }
      }
    ]
  }
}

// Create Azure Container Registry
resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: location
  tags: tags
  sku: {
    name: 'Standard'
  }
  properties: {
    adminUserEnabled: false
    networkRuleSet: {
      defaultAction: 'Deny'
      virtualNetworkRules: [
        {
          action: 'Allow'
          virtualNetworkResourceId: vnet.id
        }
      ]
    }
  }
}

// Create Azure Database for PostgreSQL
resource postgres 'Microsoft.DBforPostgreSQL/flexibleServers@2023-03-01-preview' = {
  name: postgresName
  location: location
  tags: tags
  sku: {
    name: postgresSku
  }
  properties: {
    version: '15'
    administratorLogin: 'azureshieldadmin'
    administratorLoginPassword: '@Microsoft.KeyVault(SecretUri=${keyVault.properties.vaultUri}secrets/postgres-admin-password/)'
    storage: {
      storageSizeGB: 32
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: environmentName == 'prod' ? 'Enabled' : 'Disabled'
    }
    network: {
      delegatedSubnetResourceId: vnet.properties.subnets[0].id
      privateDnsZoneArmResourceId: privateDnsZone.id
    }
  }
}

// Create Azure Cache for Redis
resource redis 'Microsoft.Cache/redis@2023-08-01' = {
  name: redisName
  location: location
  tags: tags
  properties: {
    sku: {
      name: redisSku
    }
    enableNonSslPort: false
    minimumTlsVersion: '1.2'
    network: {
      subnetId: vnet.properties.subnets[0].id
    }
  }
}

// Create Azure Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  tags: tags
  properties: {
    enabledForDeployment: true
    enabledForTemplateDeployment: true
    enabledForDiskEncryption: true
    tenantId: subscription().tenantId
    accessPolicies: []
    sku: {
      family: 'A'
      name: 'standard'
    }
    networkAcls: {
      defaultAction: 'Deny'
      bypass: 'AzureServices'
      virtualNetworkRules: [
        {
          id: vnet.id
        }
      ]
    }
  }
}

// Create Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }
}

// Create Log Analytics Workspace
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: logAnalyticsName
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// Create AKS Cluster
resource aks 'Microsoft.ContainerService/managedClusters@2023-07-02-preview' = {
  name: aksName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    kubernetesVersion: '1.26.0'
    dnsPrefix: aksName
    agentPoolProfiles: [
      {
        name: 'nodepool1'
        count: aksNodeCount
        vmSize: 'Standard_D2s_v3'
        vnetSubnetID: vnet.properties.subnets[0].id
        mode: 'System'
      }
    ]
    networkProfile: {
      networkPlugin: 'azure'
      networkPolicy: 'azure'
    }
    addonProfiles: {
      azureKeyvaultSecretsProvider: {
        enabled: true
        config: {
          enableSecretRotation: 'true'
        }
      }
      omsagent: {
        enabled: true
        config: {
          logAnalyticsWorkspaceResourceID: logAnalytics.id
        }
      }
    }
  }
}

// Create Private DNS Zone for PostgreSQL
resource privateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: '${postgresName}.private.postgres.database.azure.com'
  location: location
  tags: tags
}

// Link Private DNS Zone to VNet
resource dnsZoneLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
  name: '${privateDnsZone.name}/link'
  location: location
  properties: {
    registrationEnabled: true
    virtualNetwork: {
      id: vnet.id
    }
  }
}

// Assign RBAC roles
resource acrPullRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aks.id, acr.id, 'acrpull')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
    principalId: aks.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// Outputs
output acrLoginServer string = acr.properties.loginServer
output aksName string = aks.name
output postgresFqdn string = postgres.properties.fullyQualifiedDomainName
output keyVaultUri string = keyVault.properties.vaultUri
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey 