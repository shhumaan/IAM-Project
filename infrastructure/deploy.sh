#!/bin/bash

# Exit on error
set -e

# Configuration
ENVIRONMENT=$1
LOCATION=${2:-"eastus"}
RESOURCE_GROUP="azureshield-${ENVIRONMENT}-rg"
DEPLOYMENT_NAME="azureshield-${ENVIRONMENT}-deploy"

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    echo "Invalid environment. Must be one of: dev, staging, prod"
    exit 1
fi

# Login to Azure
echo "Logging in to Azure..."
az login

# Create resource group if it doesn't exist
echo "Creating resource group ${RESOURCE_GROUP}..."
az group create --name ${RESOURCE_GROUP} --location ${LOCATION} || true

# Deploy infrastructure
echo "Deploying infrastructure..."
az deployment group create \
    --resource-group ${RESOURCE_GROUP} \
    --name ${DEPLOYMENT_NAME} \
    --template-file main.bicep \
    --parameters environmentName=${ENVIRONMENT} \
    --parameters location=${LOCATION}

# Get deployment outputs
echo "Getting deployment outputs..."
ACR_LOGIN_SERVER=$(az deployment group show \
    --resource-group ${RESOURCE_GROUP} \
    --name ${DEPLOYMENT_NAME} \
    --query properties.outputs.acrLoginServer.value \
    --output tsv)

AKS_NAME=$(az deployment group show \
    --resource-group ${RESOURCE_GROUP} \
    --name ${DEPLOYMENT_NAME} \
    --query properties.outputs.aksName.value \
    --output tsv)

KEY_VAULT_URI=$(az deployment group show \
    --resource-group ${RESOURCE_GROUP} \
    --name ${DEPLOYMENT_NAME} \
    --query properties.outputs.keyVaultUri.value \
    --output tsv)

# Get AKS credentials
echo "Getting AKS credentials..."
az aks get-credentials --resource-group ${RESOURCE_GROUP} --name ${AKS_NAME}

# Create namespace if it doesn't exist
echo "Creating namespace..."
kubectl create namespace azureshield-${ENVIRONMENT} || true

# Create secrets in Key Vault
echo "Creating secrets in Key Vault..."
az keyvault secret set \
    --vault-name ${KEY_VAULT_URI} \
    --name postgres-admin-password \
    --value $(openssl rand -base64 32)

# Build and push Docker images
echo "Building and pushing Docker images..."
docker build -t ${ACR_LOGIN_SERVER}/azureshield-iam-backend:latest -f docker/backend/Dockerfile .
docker build -t ${ACR_LOGIN_SERVER}/azureshield-iam-frontend:latest -f docker/frontend/Dockerfile .

az acr login --name ${ACR_LOGIN_SERVER}
docker push ${ACR_LOGIN_SERVER}/azureshield-iam-backend:latest
docker push ${ACR_LOGIN_SERVER}/azureshield-iam-frontend:latest

# Deploy application to Kubernetes
echo "Deploying application to Kubernetes..."
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/deployment-blue.yaml
kubectl apply -f k8s/service.yaml

# Wait for deployment
echo "Waiting for deployment to complete..."
kubectl rollout status deployment/azureshield-iam-blue -n azureshield-${ENVIRONMENT}

# Run database migrations
echo "Running database migrations..."
kubectl apply -f k8s/migrations.yaml
kubectl wait --for=condition=complete job/db-migration -n azureshield-${ENVIRONMENT} --timeout=300s

# Run post-deployment tests
echo "Running post-deployment tests..."
kubectl apply -f k8s/post-deployment-tests.yaml
kubectl wait --for=condition=complete job/post-deployment-tests -n azureshield-${ENVIRONMENT} --timeout=300s

# Verify deployment
echo "Verifying deployment..."
kubectl get pods -n azureshield-${ENVIRONMENT} -l app=azureshield-iam

echo "Deployment completed successfully!" 