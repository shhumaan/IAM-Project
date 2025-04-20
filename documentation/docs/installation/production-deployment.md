---
sidebar_position: 3
---

# Production Deployment

This guide covers deploying AzureShield IAM to a production environment on Azure.

## Prerequisites

- Azure subscription
- Azure CLI installed and configured
- Git
- Docker

## Deployment Architecture

In production, AzureShield IAM uses the following Azure resources:

- Azure Kubernetes Service (AKS) for container orchestration
- Azure Database for PostgreSQL
- Azure Cache for Redis
- Azure Key Vault for secrets management
- Azure Monitor for logging and monitoring
- Azure Container Registry (ACR) for Docker images

## Deployment Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/azure-shield-iam.git
cd azure-shield-iam
```

### 2. Setup Azure Resources using Bicep Templates

The infrastructure is defined using Bicep templates in the `infrastructure` directory.

```bash
# Login to Azure
az login

# Create resource group
az group create --name azureshield-iam --location eastus

# Deploy infrastructure
az deployment group create \
  --resource-group azureshield-iam \
  --template-file infrastructure/main.bicep
```

### 3. Configure Environment Variables

Create a production environment file:

```bash
cp .env.example .env.production
```

Edit `.env.production` with the appropriate values from your Azure resources.

### 4. Build and Push Docker Images

```bash
# Login to Azure Container Registry
az acr login --name <your-acr-name>

# Build and tag images
docker build -f docker/backend/Dockerfile -t <your-acr-name>.azurecr.io/azureshield/api:latest ./backend
docker build -f docker/frontend/Dockerfile -t <your-acr-name>.azurecr.io/azureshield/frontend:latest ./frontend

# Push images
docker push <your-acr-name>.azurecr.io/azureshield/api:latest
docker push <your-acr-name>.azurecr.io/azureshield/frontend:latest
```

### 5. Deploy to Kubernetes

The Kubernetes manifests are located in the `k8s` directory.

```bash
# Connect to your AKS cluster
az aks get-credentials --resource-group azureshield-iam --name azureshield-iam-aks

# Update image references in Kubernetes manifests
sed -i 's|image:.*azureshield/api.*|image: <your-acr-name>.azurecr.io/azureshield/api:latest|g' k8s/api-deployment.yaml
sed -i 's|image:.*azureshield/frontend.*|image: <your-acr-name>.azurecr.io/azureshield/frontend:latest|g' k8s/frontend-deployment.yaml

# Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/config-maps.yaml
kubectl apply -f k8s/db-service.yaml
kubectl apply -f k8s/redis-service.yaml
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/ingress.yaml
```

### 6. Run Database Migrations

```bash
# Create a job to run migrations
kubectl apply -f k8s/migration-job.yaml

# Verify job completion
kubectl get jobs -n azureshield
```

### 7. Configure Azure Monitor

Set up monitoring for your AKS cluster:

```bash
# Enable monitoring
az aks enable-addons \
    --resource-group azureshield-iam \
    --name azureshield-iam-aks \
    --addons monitoring
```

### 8. Setup DNS and TLS

Configure your domain to point to the Azure Application Gateway or Load Balancer IP address.

```bash
# Install cert-manager for TLS
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.12.0/cert-manager.yaml

# Apply Let's Encrypt ClusterIssuer
kubectl apply -f k8s/cluster-issuer.yaml

# Update ingress to use TLS
kubectl apply -f k8s/ingress-tls.yaml
```

## Security Considerations

For a production deployment, ensure:

1. **Secrets Management**:
   - Store credentials in Azure Key Vault
   - Use Kubernetes secrets for sensitive information
   - Rotate credentials regularly

2. **Network Security**:
   - Implement network policies
   - Use private endpoints for Azure services
   - Configure Web Application Firewall (WAF)

3. **Monitoring and Logging**:
   - Enable Azure Monitor for containers
   - Set up alerts for suspicious activities
   - Implement log retention policies

4. **Backup and Disaster Recovery**:
   - Configure regular database backups
   - Implement geo-replication
   - Document disaster recovery procedures

## Scaling Considerations

To handle increased load:

1. **Horizontal Scaling**:
   ```bash
   kubectl scale deployment/api --replicas=5
   kubectl scale deployment/frontend --replicas=3
   ```

2. **Vertical Scaling**:
   - Adjust resource requests and limits in deployment manifests
   - Scale up Azure Database for PostgreSQL tier
   - Increase Azure Cache for Redis capacity

3. **Auto-scaling**:
   ```bash
   kubectl autoscale deployment api --min=3 --max=10 --cpu-percent=70
   ```

## Monitoring Production Deployment

Monitor your deployment using:

- Azure Monitor
- Prometheus for metrics
- Grafana dashboards
- Application logs in Azure Log Analytics

Access Grafana dashboards at: https://monitoring.yourdomain.com 