# AzureShield IAM Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying AzureShield IAM to Azure cloud infrastructure. The deployment process includes setting up the necessary Azure resources, configuring the application, and ensuring security best practices.

## Prerequisites

1. Azure CLI installed and configured
2. Docker installed locally
3. kubectl installed and configured
4. Azure subscription with appropriate permissions
5. Azure Container Registry (ACR) created
6. Azure Kubernetes Service (AKS) cluster created

## Infrastructure Setup

### 1. Resource Group Creation

```bash
# Create resource group
az group create --name azureshield-iam --location eastus

# Set default resource group
az config set defaults.group=azureshield-iam
```

### 2. Azure Container Registry

```bash
# Create ACR
az acr create --resource-group azureshield-iam \
    --name azureshieldacr \
    --sku Basic \
    --admin-enabled true

# Get ACR credentials
az acr credential show --name azureshieldacr
```

### 3. Azure Kubernetes Service

```bash
# Create AKS cluster
az aks create --resource-group azureshield-iam \
    --name azureshield-aks \
    --node-count 3 \
    --enable-addons monitoring \
    --generate-ssh-keys

# Get AKS credentials
az aks get-credentials --resource-group azureshield-iam --name azureshield-aks
```

### 4. Azure Database for PostgreSQL

```bash
# Create PostgreSQL server
az postgres flexible-server create \
    --resource-group azureshield-iam \
    --name azureshield-db \
    --admin-user azureshieldadmin \
    --admin-password <secure-password> \
    --sku-name Standard_B1ms

# Create database
az postgres flexible-server db create \
    --resource-group azureshield-iam \
    --server-name azureshield-db \
    --database-name azureshield
```

### 5. Azure Key Vault

```bash
# Create Key Vault
az keyvault create \
    --resource-group azureshield-iam \
    --name azureshield-kv \
    --enabled-for-disk-encryption true \
    --enabled-for-deployment true \
    --enabled-for-template-deployment true \
    --sku standard

# Add secrets
az keyvault secret set --vault-name azureshield-kv \
    --name JWT-SECRET \
    --value <jwt-secret>

az keyvault secret set --vault-name azureshield-kv \
    --name DB-PASSWORD \
    --value <db-password>
```

## Application Deployment

### 1. Build Docker Images

```bash
# Build backend image
docker build -t azureshieldacr.azurecr.io/backend:latest -f docker/backend/Dockerfile .

# Build frontend image
docker build -t azureshieldacr.azurecr.io/frontend:latest -f docker/frontend/Dockerfile .

# Push images to ACR
docker push azureshieldacr.azurecr.io/backend:latest
docker push azureshieldacr.azurecr.io/frontend:latest
```

### 2. Kubernetes Namespace

```bash
# Create namespace
kubectl create namespace azureshield

# Set context
kubectl config set-context --current --namespace=azureshield
```

### 3. Secrets Configuration

```yaml
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: azureshield-secrets
type: Opaque
data:
  JWT_SECRET: <base64-encoded-jwt-secret>
  DB_PASSWORD: <base64-encoded-db-password>
  REDIS_PASSWORD: <base64-encoded-redis-password>
```

```bash
# Apply secrets
kubectl apply -f secrets.yaml
```

### 4. Database Migration

```bash
# Run migrations
kubectl run alembic-migration \
    --image=azureshieldacr.azurecr.io/backend:latest \
    --command -- alembic upgrade head
```

### 5. Deploy Applications

```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: azureshieldacr.azurecr.io/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: azureshield-secrets
              key: DB_PASSWORD
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: azureshield-secrets
              key: JWT_SECRET
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
```

```yaml
# frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: azureshieldacr.azurecr.io/frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "https://api.azureshield-iam.com"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 10
```

```bash
# Apply deployments
kubectl apply -f backend-deployment.yaml
kubectl apply -f frontend-deployment.yaml
```

### 6. Configure Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: azureshield-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.azureshield-iam.com
    - app.azureshield-iam.com
    secretName: azureshield-tls
  rules:
  - host: api.azureshield-iam.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 8000
  - host: app.azureshield-iam.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 3000
```

```bash
# Apply ingress
kubectl apply -f ingress.yaml
```

## Monitoring Setup

### 1. Azure Monitor Configuration

```yaml
# monitoring.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: azureshield-monitor
spec:
  selector:
    matchLabels:
      app: backend
  endpoints:
  - port: metrics
    interval: 15s
```

```bash
# Apply monitoring
kubectl apply -f monitoring.yaml
```

### 2. Log Analytics Workspace

```bash
# Create Log Analytics workspace
az monitor log-analytics workspace create \
    --resource-group azureshield-iam \
    --workspace-name azureshield-logs \
    --location eastus
```

## Security Configuration

### 1. Network Policies

```yaml
# network-policies.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-policy
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8000
```

```bash
# Apply network policies
kubectl apply -f network-policies.yaml
```

### 2. Pod Security Policies

```yaml
# pod-security.yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: azureshield-psp
spec:
  privileged: false
  seLinux:
    rule: RunAsAny
  runAsUser:
    rule: MustRunAsNonRoot
  fsGroup:
    rule: RunAsAny
  volumes:
  - 'configMap'
  - 'emptyDir'
  - 'projected'
  - 'secret'
  - 'downwardAPI'
  - 'persistentVolumeClaim'
```

```bash
# Apply pod security policies
kubectl apply -f pod-security.yaml
```

## Backup and Recovery

### 1. Database Backup

```bash
# Create backup policy
az postgres flexible-server backup create \
    --resource-group azureshield-iam \
    --server-name azureshield-db \
    --backup-name daily-backup
```

### 2. Disaster Recovery

```bash
# Create recovery vault
az backup vault create \
    --resource-group azureshield-iam \
    --name azureshield-recovery \
    --location eastus
```

## Maintenance Procedures

### 1. Rolling Updates

```bash
# Update backend
kubectl rollout restart deployment backend

# Update frontend
kubectl rollout restart deployment frontend
```

### 2. Scaling

```bash
# Scale backend
kubectl scale deployment backend --replicas=5

# Scale frontend
kubectl scale deployment frontend --replicas=5
```

### 3. Monitoring

```bash
# Check pod status
kubectl get pods

# Check logs
kubectl logs -f deployment/backend
kubectl logs -f deployment/frontend

# Check metrics
kubectl top pods
```

## Troubleshooting

### Common Issues

1. **Pod Crash**
   ```bash
   # Check pod logs
   kubectl logs <pod-name>
   
   # Check pod events
   kubectl describe pod <pod-name>
   ```

2. **Database Connection**
   ```bash
   # Check database connection
   kubectl exec -it <pod-name> -- psql -h azureshield-db.postgres.database.azure.com -U azureshieldadmin
   ```

3. **Network Issues**
   ```bash
   # Check network policies
   kubectl get networkpolicies
   
   # Check ingress
   kubectl get ingress
   ```

### Health Checks

```bash
# Check application health
curl https://api.azureshield-iam.com/health
curl https://app.azureshield-iam.com/health
```

## Rollback Procedures

### 1. Deployment Rollback

```bash
# Rollback backend
kubectl rollout undo deployment/backend

# Rollback frontend
kubectl rollout undo deployment/frontend
```

### 2. Database Rollback

```bash
# Restore from backup
az postgres flexible-server restore \
    --resource-group azureshield-iam \
    --name azureshield-db \
    --source-server azureshield-db \
    --restore-point-in-time "2024-02-20T12:00:00Z"
``` 