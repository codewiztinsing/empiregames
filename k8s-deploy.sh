#!/bin/bash

# Liyu Bingo Kubernetes Deployment Script
# This script deploys the complete Liyu Bingo application to Kubernetes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="liyu-bingo"
REGISTRY="your-registry.com"  # Replace with your container registry
IMAGE_TAG="latest"
CLOUD_PATH="/var/www/empiregames"

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check if kubectl is installed
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
        exit 1
    fi
}

# Build Docker images
build_images() {
    log "Building Docker images..."
    
    # Change to cloud path
    cd ${CLOUD_PATH}
    
    # Build Django image
    info "Building Django image..."
    docker build -f Dockerfile.django -t ${REGISTRY}/liyu-bingo/django:${IMAGE_TAG} ./app
    docker push ${REGISTRY}/liyu-bingo/django:${IMAGE_TAG}
    
    # Build Bot image
    info "Building Bot image..."
    docker build -f Dockerfile.bot -t ${REGISTRY}/liyu-bingo/bot:${IMAGE_TAG} ./app
    docker push ${REGISTRY}/liyu-bingo/bot:${IMAGE_TAG}
    
    # Build Node.js image
    info "Building Node.js image..."
    docker build -f Dockerfile.nodejs -t ${REGISTRY}/liyu-bingo/nodejs:${IMAGE_TAG} ./bingo
    docker push ${REGISTRY}/liyu-bingo/nodejs:${IMAGE_TAG}
    
    # Build React image
    info "Building React image..."
    docker build -f Dockerfile.react -t ${REGISTRY}/liyu-bingo/react:${IMAGE_TAG} ./bingo
    docker push ${REGISTRY}/liyu-bingo/react:${IMAGE_TAG}
    
    log "All images built and pushed successfully!"
}

# Update image references in Kubernetes manifests
update_images() {
    log "Updating image references in Kubernetes manifests..."
    
    # Change to cloud path
    cd ${CLOUD_PATH}
    
    # Update Django deployment
    sed -i "s|liyu-bingo/django:latest|${REGISTRY}/liyu-bingo/django:${IMAGE_TAG}|g" k8s/04-django-backend.yaml
    
    # Update Bot deployment
    sed -i "s|liyu-bingo/bot:latest|${REGISTRY}/liyu-bingo/bot:${IMAGE_TAG}|g" k8s/05-telegram-bot.yaml
    
    # Update Node.js deployment
    sed -i "s|liyu-bingo/nodejs:latest|${REGISTRY}/liyu-bingo/nodejs:${IMAGE_TAG}|g" k8s/06-nodejs-server.yaml
    
    # Update React deployment
    sed -i "s|liyu-bingo/react:latest|${REGISTRY}/liyu-bingo/react:${IMAGE_TAG}|g" k8s/07-react-frontend.yaml
    
    log "Image references updated!"
}

# Deploy to Kubernetes
deploy_k8s() {
    log "Deploying to Kubernetes..."
    
    # Change to cloud path
    cd ${CLOUD_PATH}
    
    # Create namespace
    kubectl apply -f k8s/01-namespace-configmap-secret.yaml
    
    # Deploy PostgreSQL
    info "Deploying PostgreSQL..."
    kubectl apply -f k8s/02-postgres.yaml
    
    # Wait for PostgreSQL to be ready
    kubectl wait --for=condition=ready pod -l app=postgres -n ${NAMESPACE} --timeout=300s
    
    # Deploy Redis
    info "Deploying Redis..."
    kubectl apply -f k8s/03-redis.yaml
    
    # Wait for Redis to be ready
    kubectl wait --for=condition=ready pod -l app=redis -n ${NAMESPACE} --timeout=300s
    
    # Deploy Django Backend
    info "Deploying Django Backend..."
    kubectl apply -f k8s/04-django-backend.yaml
    
    # Wait for Django to be ready
    kubectl wait --for=condition=ready pod -l app=django-backend -n ${NAMESPACE} --timeout=300s
    
    # Deploy Telegram Bot
    info "Deploying Telegram Bot..."
    kubectl apply -f k8s/05-telegram-bot.yaml
    
    # Deploy Node.js Server
    info "Deploying Node.js Server..."
    kubectl apply -f k8s/06-nodejs-server.yaml
    
    # Wait for Node.js to be ready
    kubectl wait --for=condition=ready pod -l app=nodejs-server -n ${NAMESPACE} --timeout=300s
    
    # Deploy React Frontend
    info "Deploying React Frontend..."
    kubectl apply -f k8s/07-react-frontend.yaml
    
    # Wait for React to be ready
    kubectl wait --for=condition=ready pod -l app=react-frontend -n ${NAMESPACE} --timeout=300s
    
    # Deploy RabbitMQ
    info "Deploying RabbitMQ..."
    kubectl apply -f k8s/11-rabbitmq-celery.yaml
    
    # Wait for RabbitMQ to be ready
    kubectl wait --for=condition=ready pod -l app=rabbitmq -n ${NAMESPACE} --timeout=300s
    
    # Wait for Celery to be ready
    kubectl wait --for=condition=ready pod -l app=celery-worker -n ${NAMESPACE} --timeout=300s
    kubectl wait --for=condition=ready pod -l app=celery-beat -n ${NAMESPACE} --timeout=300s
    kubectl wait --for=condition=ready pod -l app=celery-flower -n ${NAMESPACE} --timeout=300s
    
    # Deploy Ingress
    info "Deploying Ingress..."
    kubectl apply -f k8s/08-ingress.yaml
    
    log "Deployment completed successfully!"
}

# Check deployment status
check_status() {
    log "Checking deployment status..."
    
    echo ""
    info "Namespace:"
    kubectl get namespace ${NAMESPACE}
    
    echo ""
    info "Pods:"
    kubectl get pods -n ${NAMESPACE}
    
    echo ""
    info "Services:"
    kubectl get services -n ${NAMESPACE}
    
    echo ""
    info "Ingress:"
    kubectl get ingress -n ${NAMESPACE}
    
    echo ""
    info "Horizontal Pod Autoscalers:"
    kubectl get hpa -n ${NAMESPACE}
}

# Scale deployments
scale_deployments() {
    local django_replicas=${1:-3}
    local bot_replicas=${2:-2}
    local nodejs_replicas=${3:-3}
    local react_replicas=${4:-3}
    local celery_replicas=${5:-3}
    
    log "Scaling deployments..."
    
    kubectl scale deployment django-backend --replicas=${django_replicas} -n ${NAMESPACE}
    kubectl scale deployment telegram-bot --replicas=${bot_replicas} -n ${NAMESPACE}
    kubectl scale deployment nodejs-server --replicas=${nodejs_replicas} -n ${NAMESPACE}
    kubectl scale deployment react-frontend --replicas=${react_replicas} -n ${NAMESPACE}
    kubectl scale deployment celery-worker --replicas=${celery_replicas} -n ${NAMESPACE}
    
    log "Deployments scaled successfully!"
}

# Rollback deployment
rollback() {
    log "Rolling back deployment..."
    
    kubectl rollout undo deployment django-backend -n ${NAMESPACE}
    kubectl rollout undo deployment telegram-bot -n ${NAMESPACE}
    kubectl rollout undo deployment nodejs-server -n ${NAMESPACE}
    kubectl rollout undo deployment react-frontend -n ${NAMESPACE}
    kubectl rollout undo deployment rabbitmq -n ${NAMESPACE}
    kubectl rollout undo deployment celery-worker -n ${NAMESPACE}
    kubectl rollout undo deployment celery-beat -n ${NAMESPACE}
    kubectl rollout undo deployment celery-flower -n ${NAMESPACE}
    
    log "Rollback completed!"
}

# Clean up deployment
cleanup() {
    log "Cleaning up deployment..."
    
    kubectl delete namespace ${NAMESPACE}
    
    log "Cleanup completed!"
}

# Show logs
show_logs() {
    local service=${1:-"all"}
    
    case $service in
        "django")
            kubectl logs -l app=django-backend -n ${NAMESPACE} --tail=100
            ;;
        "bot")
            kubectl logs -l app=telegram-bot -n ${NAMESPACE} --tail=100
            ;;
        "nodejs")
            kubectl logs -l app=nodejs-server -n ${NAMESPACE} --tail=100
            ;;
        "react")
            kubectl logs -l app=react-frontend -n ${NAMESPACE} --tail=100
            ;;
        "rabbitmq")
            kubectl logs -l app=rabbitmq -n ${NAMESPACE} --tail=100
            ;;
        "celery")
            kubectl logs -l app=celery-worker -n ${NAMESPACE} --tail=100
            ;;
        "celery-beat")
            kubectl logs -l app=celery-beat -n ${NAMESPACE} --tail=100
            ;;
        "celery-flower")
            kubectl logs -l app=celery-flower -n ${NAMESPACE} --tail=100
            ;;
        "all")
            kubectl logs -l app=django-backend -n ${NAMESPACE} --tail=50
            echo "---"
            kubectl logs -l app=telegram-bot -n ${NAMESPACE} --tail=50
            echo "---"
            kubectl logs -l app=nodejs-server -n ${NAMESPACE} --tail=50
            echo "---"
            kubectl logs -l app=react-frontend -n ${NAMESPACE} --tail=50
            echo "---"
            kubectl logs -l app=rabbitmq -n ${NAMESPACE} --tail=50
            echo "---"
            kubectl logs -l app=celery-worker -n ${NAMESPACE} --tail=50
            echo "---"
            kubectl logs -l app=celery-beat -n ${NAMESPACE} --tail=50
            echo "---"
            kubectl logs -l app=celery-flower -n ${NAMESPACE} --tail=50
            ;;
        *)
            error "Invalid service. Use: django, bot, nodejs, react, rabbitmq, celery, celery-beat, celery-flower, or all"
            exit 1
            ;;
    esac
}

# Main function
main() {
    case "${1:-deploy}" in
        "build")
            check_docker
            build_images
            ;;
        "deploy")
            check_kubectl
            update_images
            deploy_k8s
            check_status
            ;;
        "status")
            check_status
            ;;
        "scale")
            scale_deployments $2 $3 $4 $5
            ;;
        "rollback")
            rollback
            ;;
        "logs")
            show_logs $2
            ;;
        "cleanup")
            cleanup
            ;;
        "full-deploy")
            check_docker
            check_kubectl
            build_images
            update_images
            deploy_k8s
            check_status
            ;;
        *)
            echo "Usage: $0 {build|deploy|status|scale|rollback|logs|cleanup|full-deploy}"
            echo ""
            echo "Commands:"
            echo "  build        - Build and push Docker images"
            echo "  deploy       - Deploy to Kubernetes"
            echo "  status       - Check deployment status"
            echo "  scale        - Scale deployments (django bot nodejs react celery)"
            echo "  rollback     - Rollback to previous version"
            echo "  logs         - Show logs (django|bot|nodejs|react|rabbitmq|celery|celery-beat|celery-flower|all)"
            echo "  cleanup      - Clean up deployment"
            echo "  full-deploy  - Build, push, and deploy everything"
            echo ""
            echo "Examples:"
            echo "  $0 full-deploy"
            echo "  $0 scale 5 3 5 3 5"
            echo "  $0 logs celery"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
