# Liyu Bingo Kubernetes Cloud Deployment Guide

## Overview
This guide covers deploying the Liyu Bingo application to Kubernetes using your cloud code at `/var/www/empiregames`.

## Prerequisites
- Kubernetes cluster (EKS, GKE, AKS, or self-managed)
- kubectl configured
- Docker installed
- Container registry access
- Domain name with SSL certificate

## Cloud Setup

### 1. Server Configuration
```bash
# Your cloud code is located at
CLOUD_PATH="/var/www/empiregames"

# Directory structure:
/var/www/empiregames/
├── app/                    # Django backend
├── bingo/                  # Node.js server + React frontend
├── k8s/                    # Kubernetes manifests
├── Dockerfile.django       # Django container
├── Dockerfile.bot          # Telegram bot container
├── Dockerfile.nodejs       # Node.js container
├── Dockerfile.react        # React container
└── k8s-deploy.sh          # Deployment script
```

### 2. Environment Configuration
```bash
# Update the deployment script configuration
cd /var/www/empiregames

# Edit k8s-deploy.sh
nano k8s-deploy.sh

# Update these variables:
REGISTRY="your-registry.com"  # Your container registry
IMAGE_TAG="v1.0.0"           # Version tag
CLOUD_PATH="/var/www/empiregames"  # Already set
```

### 3. Container Registry Setup
```bash
# Login to your container registry
docker login your-registry.com

# Or use cloud-specific commands:
# AWS ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-west-2.amazonaws.com

# Google GCR
gcloud auth configure-docker

# Azure ACR
az acr login --name your-registry
```

## Deployment Steps

### 1. Initial Setup
```bash
# Navigate to your cloud code
cd /var/www/empiregames

# Make deployment script executable
chmod +x k8s-deploy.sh

# Update secrets in Kubernetes manifests
nano k8s/01-namespace-configmap-secret.yaml

# Update these values with base64 encoded secrets:
BOT_TOKEN=your-actual-bot-token-base64
POSTGRES_PASSWORD=your-secure-password-base64
MANUAL_API_KEY=your-manual-api-key-base64
MANUAL_BASE_URL=your-manual-base-url-base64
```

### 2. Build and Deploy
```bash
# Full deployment (build, push, deploy)
./k8s-deploy.sh full-deploy

# Or step by step:
./k8s-deploy.sh build      # Build and push images
./k8s-deploy.sh deploy     # Deploy to Kubernetes
./k8s-deploy.sh status     # Check status
```

### 3. Verify Deployment
```bash
# Check all resources
kubectl get all -n liyu-bingo

# Check specific services
kubectl get pods -n liyu-bingo
kubectl get services -n liyu-bingo
kubectl get ingress -n liyu-bingo
kubectl get hpa -n liyu-bingo

# Check logs
./k8s-deploy.sh logs all
```

## Horizontal Scaling

### 1. Automatic Scaling (HPA)
The deployment includes Horizontal Pod Autoscalers (HPA) for:
- **Django Backend**: 3-10 replicas (CPU/Memory based)
- **Telegram Bot**: 2-5 replicas (CPU/Memory based)
- **Node.js Server**: 3-15 replicas (CPU/Memory based)
- **React Frontend**: 3-10 replicas (CPU/Memory based)

### 2. Manual Scaling
```bash
# Scale specific services
./k8s-deploy.sh scale 5 3 5 3  # django bot nodejs react

# Scale individual deployments
kubectl scale deployment django-backend --replicas=5 -n liyu-bingo
kubectl scale deployment telegram-bot --replicas=3 -n liyu-bingo
kubectl scale deployment nodejs-server --replicas=5 -n liyu-bingo
kubectl scale deployment react-frontend --replicas=3 -n liyu-bingo
```

### 3. Custom Scaling Policies
```bash
# Update HPA configurations
kubectl edit hpa django-hpa -n liyu-bingo
kubectl edit hpa bot-hpa -n liyu-bingo
kubectl edit hpa nodejs-hpa -n liyu-bingo
kubectl edit hpa react-hpa -n liyu-bingo
```

## Monitoring and Maintenance

### 1. Health Checks
```bash
# Check pod health
kubectl get pods -n liyu-bingo -o wide

# Check service endpoints
kubectl get endpoints -n liyu-bingo

# Check ingress status
kubectl describe ingress liyu-bingo-ingress -n liyu-bingo
```

### 2. Logs and Debugging
```bash
# View logs for specific services
./k8s-deploy.sh logs django
./k8s-deploy.sh logs bot
./k8s-deploy.sh logs nodejs
./k8s-deploy.sh logs react

# Follow logs in real-time
kubectl logs -f deployment/django-backend -n liyu-bingo
kubectl logs -f deployment/telegram-bot -n liyu-bingo
kubectl logs -f deployment/nodejs-server -n liyu-bingo
kubectl logs -f deployment/react-frontend -n liyu-bingo
```

### 3. Resource Monitoring
```bash
# Check resource usage
kubectl top pods -n liyu-bingo
kubectl top nodes

# Check HPA status
kubectl get hpa -n liyu-bingo
kubectl describe hpa django-hpa -n liyu-bingo
```

## Updates and Rollbacks

### 1. Rolling Updates
```bash
# Update images
docker build -f Dockerfile.django -t your-registry.com/liyu-bingo/django:v1.0.1 ./app
docker push your-registry.com/liyu-bingo/django:v1.0.1

# Update deployment
kubectl set image deployment/django-backend django=your-registry.com/liyu-bingo/django:v1.0.1 -n liyu-bingo

# Check rollout status
kubectl rollout status deployment/django-backend -n liyu-bingo
```

### 2. Rollbacks
```bash
# Rollback to previous version
./k8s-deploy.sh rollback

# Or manual rollback
kubectl rollout undo deployment/django-backend -n liyu-bingo
kubectl rollout undo deployment/telegram-bot -n liyu-bingo
kubectl rollout undo deployment/nodejs-server -n liyu-bingo
kubectl rollout undo deployment/react-frontend -n liyu-bingo
```

## Cloud-Specific Configurations

### 1. AWS EKS
```bash
# Update k8s-deploy.sh for EKS
REGISTRY="your-account.dkr.ecr.us-west-2.amazonaws.com"

# Use EKS load balancer
kubectl apply -f k8s/aws-loadbalancer.yaml
```

### 2. Google GKE
```bash
# Update k8s-deploy.sh for GKE
REGISTRY="gcr.io/your-project-id"

# Use GKE ingress
kubectl apply -f k8s/gke-ingress.yaml
```

### 3. Azure AKS
```bash
# Update k8s-deploy.sh for AKS
REGISTRY="your-registry.azurecr.io"

# Use AKS ingress
kubectl apply -f k8s/aks-ingress.yaml
```

## Security Considerations

### 1. Network Policies
```bash
# Apply network policies
kubectl apply -f k8s/08-ingress.yaml  # Includes network policies
```

### 2. Secrets Management
```bash
# Use cloud-specific secret management
# AWS Secrets Manager
kubectl create secret generic liyu-secrets \
  --from-literal=BOT_TOKEN=$(aws secretsmanager get-secret-value --secret-id bot-token --query SecretString --output text) \
  -n liyu-bingo

# Google Secret Manager
kubectl create secret generic liyu-secrets \
  --from-literal=BOT_TOKEN=$(gcloud secrets versions access latest --secret="bot-token") \
  -n liyu-bingo
```

### 3. RBAC
```bash
# Create service accounts and RBAC
kubectl apply -f k8s/rbac.yaml
```

## Troubleshooting

### Common Issues

1. **Pod Startup Issues**
   ```bash
   kubectl describe pod <pod-name> -n liyu-bingo
   kubectl logs <pod-name> -n liyu-bingo
   ```

2. **Service Connection Issues**
   ```bash
   kubectl get services -n liyu-bingo
   kubectl describe service <service-name> -n liyu-bingo
   ```

3. **Ingress Issues**
   ```bash
   kubectl describe ingress liyu-bingo-ingress -n liyu-bingo
   kubectl get ingress -n liyu-bingo
   ```

4. **HPA Issues**
   ```bash
   kubectl describe hpa <hpa-name> -n liyu-bingo
   kubectl get events -n liyu-bingo
   ```

### Performance Optimization

1. **Resource Limits**
   ```bash
   # Update resource limits in deployments
   kubectl edit deployment django-backend -n liyu-bingo
   kubectl edit deployment nodejs-server -n liyu-bingo
   ```

2. **Node Affinity**
   ```bash
   # Add node affinity for better performance
   kubectl apply -f k8s/node-affinity.yaml
   ```

3. **Pod Disruption Budgets**
   ```bash
   # Ensure availability during updates
   kubectl apply -f k8s/pdb.yaml
   ```

## Cleanup

```bash
# Remove all resources
./k8s-deploy.sh cleanup

# Or manual cleanup
kubectl delete namespace liyu-bingo
```

## Support

For issues and support:
- Check logs: `./k8s-deploy.sh logs all`
- Check status: `./k8s-deploy.sh status`
- Check events: `kubectl get events -n liyu-bingo`
- Check resources: `kubectl top pods -n liyu-bingo`
