# Deployment Guide
## Unified AI Business Assistant for CNC Factory

**Version:** 1.0  
**Last Updated:** 2024  
**Audience:** DevOps Engineers, System Administrators

---

## Table of Contents

1. [Overview](#overview)
2. [Infrastructure Requirements](#infrastructure-requirements)
3. [Pre-Deployment Checklist](#pre-deployment-checklist)
4. [Environment Setup](#environment-setup)
5. [Application Deployment](#application-deployment)
6. [Database Setup](#database-setup)
7. [Third-Party Services Configuration](#third-party-services-configuration)
8. [Security Configuration](#security-configuration)
9. [Monitoring & Logging](#monitoring--logging)
10. [Backup & Disaster Recovery](#backup--disaster-recovery)
11. [Scaling & Performance](#scaling--performance)
12. [Maintenance & Updates](#maintenance--updates)
13. [Troubleshooting](#troubleshooting)

---

## Overview

This guide provides step-by-step instructions for deploying the Unified AI Business Assistant application to production. The deployment uses modern cloud-native practices with containerization and orchestration.

### Deployment Architecture

```
┌─────────────────────────────────────────────────────┐
│              Cloud Provider (AWS/Azure/GCP)         │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │         Kubernetes Cluster                    │  │
│  │  ┌──────────────┐  ┌──────────────┐          │  │
│  │  │   Ingress    │  │  Load        │          │  │
│  │  │   Controller │  │  Balancer    │          │  │
│  │  └──────────────┘  └──────────────┘          │  │
│  │         │                │                    │  │
│  │  ┌──────────────────────────────────────┐    │  │
│  │  │  Application Pods                    │    │  │
│  │  │  ┌─────┐  ┌─────┐  ┌─────┐          │    │  │
│  │  │  │ API │  │Web  │  │Work │          │    │  │
│  │  │  │ Pod │  │ Pod │  │ Pod │          │    │  │
│  │  │  └─────┘  └─────┘  └─────┘          │    │  │
│  │  └──────────────────────────────────────┘    │  │
│  │         │                │                    │  │
│  │  ┌──────────────────────────────────────┐    │  │
│  │  │  Service Mesh (Istio) - Optional     │    │  │
│  │  └──────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────┘  │
│         │                │                │        │
│  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐│
│  │ PostgreSQL  │  │    Redis    │  │Elasticsearch││
│  │  (Primary)  │  │   (Cache)   │  │   (Search)  ││
│  └─────────────┘  └─────────────┘  └─────────────┘│
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │  Object Storage (S3/Blob/GCS)                │  │
│  │  - Documents                                  │  │
│  │  - User uploads                              │  │
│  │  - Backups                                   │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## Infrastructure Requirements

### Cloud Provider Options

**Recommended:** AWS, Azure, or Google Cloud Platform

### Compute Resources

**Minimum (Small Deployment):**
- **API Servers:** 2x (4 CPU, 8GB RAM each)
- **Web Servers:** 2x (2 CPU, 4GB RAM each)
- **Workers:** 2x (4 CPU, 8GB RAM each)

**Recommended (Medium Deployment):**
- **API Servers:** 3-5x (8 CPU, 16GB RAM each)
- **Web Servers:** 3x (4 CPU, 8GB RAM each)
- **Workers:** 3-5x (8 CPU, 16GB RAM each)

**Production (Large Deployment):**
- **API Servers:** 5-10x (16 CPU, 32GB RAM each)
- **Web Servers:** 5x (8 CPU, 16GB RAM each)
- **Workers:** 5-10x (16 CPU, 32GB RAM each)
- **Auto-scaling enabled**

### Database Resources

**PostgreSQL (Primary):**
- **Small:** 4 CPU, 16GB RAM, 500GB SSD
- **Medium:** 8 CPU, 32GB RAM, 1TB SSD
- **Large:** 16 CPU, 64GB RAM, 2TB SSD + Read Replicas

**Redis (Cache):**
- **Small:** 2 CPU, 4GB RAM
- **Medium:** 4 CPU, 8GB RAM
- **Large:** 8 CPU, 16GB RAM (Cluster mode)

**Elasticsearch (Search):**
- **Small:** 4 CPU, 16GB RAM, 500GB SSD
- **Medium:** 8 CPU, 32GB RAM, 1TB SSD
- **Large:** 16 CPU, 64GB RAM, 2TB SSD (Cluster)

### Storage

**Object Storage:**
- **Documents:** 1TB+ (grows with usage)
- **Backups:** 5TB+ (with retention)

**Network:**
- **Bandwidth:** 1Gbps+ recommended
- **CDN:** For static assets (optional but recommended)

### DNS & SSL

- **Domain name** configured
- **SSL certificates** (Let's Encrypt or commercial)
- **DNS records** configured

---

## Pre-Deployment Checklist

### Prerequisites

- [ ] Cloud provider account created and configured
- [ ] Domain name registered and DNS access
- [ ] SSL certificates obtained
- [ ] Third-party API keys obtained (see list below)
- [ ] Team access to cloud provider console
- [ ] CI/CD pipeline configured
- [ ] Monitoring tools accounts created
- [ ] Backup storage configured

### Third-Party Services

**Required:**
- [ ] **Email Service:** SendGrid / AWS SES / Azure Communication Services
- [ ] **OCR Service:** Google Cloud Vision / AWS Textract / Azure Computer Vision
- [ ] **AI/LLM Service:** OpenAI API / Anthropic Claude / AWS Bedrock
- [ ] **Payment Gateway:** Stripe / PayPal (if processing payments)
- [ ] **Object Storage:** AWS S3 / Azure Blob / Google Cloud Storage

**Optional:**
- [ ] **SMS Service:** Twilio (for SMS notifications)
- [ ] **Shipping API:** Carrier APIs (if integrating shipping)
- [ ] **Analytics:** Google Analytics / Mixpanel

### Security

- [ ] SSH keys generated
- [ ] VPN access configured (if on-premise access needed)
- [ ] Firewall rules defined
- [ ] Security groups configured
- [ ] Secrets management system ready (AWS Secrets Manager / Azure Key Vault / HashiCorp Vault)

---

## Environment Setup

### Cloud Provider Setup (AWS Example)

#### 1. Create VPC

```bash
# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=unified-ai-vpc}]'

# Create subnets (public and private)
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.1.0/24 --availability-zone us-east-1a
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.2.0/24 --availability-zone us-east-1b
```

#### 2. Create Kubernetes Cluster (EKS)

```bash
# Install eksctl
brew install eksctl  # or download from GitHub

# Create cluster
eksctl create cluster \
  --name unified-ai-cluster \
  --region us-east-1 \
  --nodegroup-name standard-workers \
  --node-type t3.2xlarge \
  --nodes 3 \
  --nodes-min 3 \
  --nodes-max 10 \
  --managed
```

### Install Required Tools

#### Kubernetes CLI (kubectl)

```bash
# macOS
brew install kubectl

# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Verify
kubectl version --client
```

#### Helm (Package Manager)

```bash
# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify
helm version
```

#### Docker

```bash
# Install Docker Desktop or Docker Engine
# Verify
docker --version
```

---

## Application Deployment

### Step 1: Container Registry Setup

#### Create Container Registry

**AWS ECR:**
```bash
aws ecr create-repository --repository-name unified-ai-api --region us-east-1
aws ecr create-repository --repository-name unified-ai-web --region us-east-1
aws ecr create-repository --repository-name unified-ai-worker --region us-east-1
```

**Docker Hub / Azure Container Registry / Google Container Registry:**
- Follow provider-specific documentation

### Step 2: Build and Push Docker Images

#### Build Images

```bash
# Navigate to project root
cd /path/to/unified-ai-assistant

# Build API image
docker build -t unified-ai-api:latest -f docker/api/Dockerfile .
docker tag unified-ai-api:latest <registry>/unified-ai-api:v1.0.0

# Build Web image
docker build -t unified-ai-web:latest -f docker/web/Dockerfile .
docker tag unified-ai-web:latest <registry>/unified-ai-web:v1.0.0

# Build Worker image
docker build -t unified-ai-worker:latest -f docker/worker/Dockerfile .
docker tag unified-ai-worker:latest <registry>/unified-ai-worker:v1.0.0
```

#### Push to Registry

```bash
# Login to registry
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

# Push images
docker push <registry>/unified-ai-api:v1.0.0
docker push <registry>/unified-ai-web:v1.0.0
docker push <registry>/unified-ai-worker:v1.0.0
```

### Step 3: Deploy to Kubernetes

#### Create Namespace

```bash
kubectl create namespace unified-ai-production
```

#### Create Secrets

```bash
# Create secret for database
kubectl create secret generic db-credentials \
  --from-literal=username=postgres \
  --from-literal=password=<secure-password> \
  --namespace unified-ai-production

# Create secret for API keys
kubectl create secret generic api-keys \
  --from-literal=openai-key=<key> \
  --from-literal=sendgrid-key=<key> \
  --from-literal=jwt-secret=<secret> \
  --namespace unified-ai-production
```

#### Deploy with Helm Chart

**Create values.yaml:**
```yaml
# values.yaml
replicaCount: 3

image:
  repository: <registry>/unified-ai-api
  tag: v1.0.0
  pullPolicy: IfNotPresent

database:
  host: postgres-service
  port: 5432
  name: unified_ai
  usernameSecret: db-credentials
  passwordSecret: db-credentials

redis:
  host: redis-service
  port: 6379

resources:
  requests:
    cpu: 500m
    memory: 1Gi
  limits:
    cpu: 2000m
    memory: 4Gi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
```

**Deploy:**
```bash
# Install Helm chart
helm install unified-ai ./helm-charts/unified-ai \
  --namespace unified-ai-production \
  --values values.yaml
```

#### Manual Kubernetes Deployment (Alternative)

**API Deployment:**
```yaml
# api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: unified-ai-api
  namespace: unified-ai-production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: unified-ai-api
  template:
    metadata:
      labels:
        app: unified-ai-api
    spec:
      containers:
      - name: api
        image: <registry>/unified-ai-api:v1.0.0
        ports:
        - containerPort: 3000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 4Gi
---
apiVersion: v1
kind: Service
metadata:
  name: unified-ai-api-service
  namespace: unified-ai-production
spec:
  selector:
    app: unified-ai-api
  ports:
  - port: 80
    targetPort: 3000
  type: ClusterIP
```

```bash
kubectl apply -f api-deployment.yaml
```

### Step 4: Ingress Configuration

#### Install Ingress Controller (NGINX)

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

#### Create Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: unified-ai-ingress
  namespace: unified-ai-production
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - app.unified-ai-assistant.com
    - api.unified-ai-assistant.com
    secretName: unified-ai-tls
  rules:
  - host: app.unified-ai-assistant.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: unified-ai-web-service
            port:
              number: 80
  - host: api.unified-ai-assistant.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: unified-ai-api-service
            port:
              number: 80
```

```bash
kubectl apply -f ingress.yaml
```

---

## Database Setup

### PostgreSQL Setup

#### Option 1: Managed Database (Recommended)

**AWS RDS:**
```bash
aws rds create-db-instance \
  --db-instance-identifier unified-ai-db \
  --db-instance-class db.r5.xlarge \
  --engine postgres \
  --engine-version 15.4 \
  --master-username postgres \
  --master-user-password <secure-password> \
  --allocated-storage 500 \
  --storage-type gp2 \
  --vpc-security-group-ids sg-xxx \
  --db-subnet-group-name unified-ai-db-subnet-group \
  --backup-retention-period 7 \
  --multi-az
```

**Azure Database for PostgreSQL:**
- Use Azure Portal or Azure CLI
- Create Flexible Server instance
- Configure networking and security

**Google Cloud SQL:**
```bash
gcloud sql instances create unified-ai-db \
  --database-version=POSTGRES_15 \
  --tier=db-custom-8-32768 \
  --region=us-east1 \
  --storage-type=SSD \
  --storage-size=500GB \
  --backup-start-time=03:00
```

#### Option 2: Self-Managed (Kubernetes)

**Deploy PostgreSQL with Helm:**
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install postgresql bitnami/postgresql \
  --namespace unified-ai-production \
  --set postgresqlPassword=<password> \
  --set postgresqlDatabase=unified_ai \
  --set persistence.size=500Gi
```

### Database Initialization

#### Run Migrations

```bash
# Get database connection details
DB_HOST=<db-host>
DB_NAME=unified_ai
DB_USER=postgres
DB_PASSWORD=<password>

# Run migrations
kubectl run migration-job \
  --image=<registry>/unified-ai-api:v1.0.0 \
  --namespace unified-ai-production \
  --env="DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:5432/$DB_NAME" \
  --command -- npm run migrate

# Or use Kubernetes Job
kubectl apply -f migration-job.yaml
```

**Migration Job YAML:**
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: database-migration
  namespace: unified-ai-production
spec:
  template:
    spec:
      containers:
      - name: migrate
        image: <registry>/unified-ai-api:v1.0.0
        command: ["npm", "run", "migrate"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
      restartPolicy: Never
  backoffLimit: 3
```

#### Seed Initial Data

```bash
kubectl run seed-job \
  --image=<registry>/unified-ai-api:v1.0.0 \
  --namespace unified-ai-production \
  --command -- npm run seed
```

### Redis Setup

#### Deploy Redis

```bash
helm install redis bitnami/redis \
  --namespace unified-ai-production \
  --set auth.password=<redis-password> \
  --set master.persistence.size=50Gi
```

### Elasticsearch Setup

#### Deploy Elasticsearch

```bash
helm repo add elastic https://helm.elastic.co
helm install elasticsearch elastic/elasticsearch \
  --namespace unified-ai-production \
  --set replicas=3 \
  --set resources.requests.memory=16Gi \
  --set resources.limits.memory=32Gi
```

---

## Third-Party Services Configuration

### Email Service (SendGrid)

#### Setup SendGrid

1. Create SendGrid account
2. Generate API key
3. Verify sender domain
4. Configure DNS records (SPF, DKIM)

**Configure in Application:**
```bash
kubectl create secret generic sendgrid \
  --from-literal=api-key=<sendgrid-api-key> \
  --namespace unified-ai-production
```

### OCR Service (Google Cloud Vision)

#### Setup Google Cloud Vision

1. Create GCP project
2. Enable Vision API
3. Create service account
4. Download credentials JSON

**Configure:**
```bash
kubectl create secret generic gcp-credentials \
  --from-file=credentials.json=<path-to-credentials.json> \
  --namespace unified-ai-production
```

### AI/LLM Service (OpenAI)

#### Setup OpenAI

1. Create OpenAI account
2. Generate API key
3. Set up billing

**Configure:**
```bash
kubectl create secret generic openai \
  --from-literal=api-key=<openai-api-key> \
  --namespace unified-ai-production
```

### Object Storage (AWS S3)

#### Create S3 Buckets

```bash
# Documents bucket
aws s3 mb s3://unified-ai-documents-prod --region us-east-1

# Backups bucket
aws s3 mb s3://unified-ai-backups-prod --region us-east-1

# Configure lifecycle policies
aws s3api put-bucket-lifecycle-configuration \
  --bucket unified-ai-documents-prod \
  --lifecycle-configuration file://lifecycle.json
```

**Configure IAM:**
```bash
# Create IAM user for application
aws iam create-user --user-name unified-ai-app

# Attach policy for S3 access
aws iam attach-user-policy \
  --user-name unified-ai-app \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```

---

## Security Configuration

### SSL/TLS Certificates

#### Using cert-manager (Let's Encrypt)

**Install cert-manager:**
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

**Create ClusterIssuer:**
```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@unified-ai-assistant.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

### Network Policies

**Create Network Policy:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-network-policy
  namespace: unified-ai-production
spec:
  podSelector:
    matchLabels:
      app: unified-ai-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 3000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgresql
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
```

### Secrets Management

**Use External Secrets Operator:**
```bash
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets \
  --namespace external-secrets-system \
  --create-namespace
```

### Firewall Rules

**AWS Security Groups:**
- Allow HTTP (80) from internet
- Allow HTTPS (443) from internet
- Allow SSH (22) from VPN/bastion only
- Database: Only from application servers

---

## Monitoring & Logging

### Application Monitoring (Prometheus + Grafana)

#### Install Prometheus

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

#### Install Grafana

```bash
# Already included in kube-prometheus-stack
# Access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
# Login: admin / prom-operator
```

### Application Logging (ELK Stack)

#### Install Elasticsearch (if not already installed)

#### Install Logstash

```bash
helm install logstash elastic/logstash \
  --namespace logging \
  --create-namespace
```

#### Install Kibana

```bash
helm install kibana elastic/kibana \
  --namespace logging
```

### Application Insights

**Configure APM (Application Performance Monitoring):**
- Use DataDog, New Relic, or Elastic APM
- Install agents in application containers
- Configure dashboards and alerts

---

## Backup & Disaster Recovery

### Database Backups

#### Automated Backups (RDS)

**RDS automatically backs up:**
- Daily automated backups (7-35 days retention)
- Point-in-time recovery enabled
- Cross-region replication (optional)

#### Manual Backup Script

```bash
#!/bin/bash
# backup-database.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_$DATE.sql"
S3_BUCKET="s3://unified-ai-backups-prod/database/"

# Create backup
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $BACKUP_FILE

# Compress
gzip $BACKUP_FILE

# Upload to S3
aws s3 cp "$BACKUP_FILE.gz" $S3_BUCKET

# Cleanup
rm "$BACKUP_FILE.gz"

echo "Backup completed: $BACKUP_FILE.gz"
```

#### Restore from Backup

```bash
# Download backup
aws s3 cp s3://unified-ai-backups-prod/database/backup_20240115_120000.sql.gz .

# Decompress
gunzip backup_20240115_120000.sql.gz

# Restore
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < backup_20240115_120000.sql
```

### Disaster Recovery Plan

**Recovery Time Objective (RTO):** 4 hours  
**Recovery Point Objective (RPO):** 1 hour

**Recovery Steps:**
1. **Failover to DR Region:**
   - DNS failover to secondary region
   - Activate secondary database (read replica promotion)
   - Scale up DR infrastructure

2. **Data Restoration:**
   - Restore latest backup
   - Replay transaction logs if needed

3. **Service Restoration:**
   - Deploy application to DR region
   - Verify functionality
   - Monitor for issues

---

## Scaling & Performance

### Horizontal Pod Autoscaling

**Already configured in Helm values:**
```yaml
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80
```

### Database Scaling

**Read Replicas:**
```bash
# Create read replica (AWS RDS)
aws rds create-db-instance-read-replica \
  --db-instance-identifier unified-ai-db-replica \
  --source-db-instance-identifier unified-ai-db \
  --db-instance-class db.r5.xlarge
```

### CDN Configuration

**CloudFront / Azure CDN / Cloud CDN:**
- Configure for static assets
- Cache headers: 1 year for assets, no cache for API

### Caching Strategy

**Redis Cache Layers:**
- Session cache: 24 hours
- API response cache: 5 minutes
- Database query cache: 1 hour
- Static content: CDN edge cache

---

## Maintenance & Updates

### Zero-Downtime Deployment

**Blue-Green Deployment:**
```bash
# Deploy new version (green)
helm upgrade unified-ai ./helm-charts/unified-ai \
  --namespace unified-ai-production \
  --values values.yaml \
  --set image.tag=v1.1.0

# Verify green deployment
kubectl get pods -n unified-ai-production

# Switch traffic (update ingress)
# If issues, rollback
helm rollback unified-ai -n unified-ai-production
```

### Database Migrations

**Strategy:**
1. Deploy migration job
2. Wait for completion
3. Deploy new application version
4. Monitor for errors
5. Rollback if needed

### Health Checks

**Liveness Probe:**
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 3000
  initialDelaySeconds: 30
  periodSeconds: 10
```

**Readiness Probe:**
```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 3000
  initialDelaySeconds: 5
  periodSeconds: 5
```

---

## Troubleshooting

### Common Issues

#### Pods Not Starting

**Symptoms:**
- Pods stuck in `Pending` or `CrashLoopBackOff` state
- Pods not ready after deployment

**Diagnosis:**
```bash
# Check pod status
kubectl get pods -n unified-ai-production

# Check logs
kubectl logs <pod-name> -n unified-ai-production

# Describe pod for events
kubectl describe pod <pod-name> -n unified-ai-production

# Check events
kubectl get events -n unified-ai-production --sort-by='.lastTimestamp'
```

**Common Causes & Solutions:**

1. **Insufficient Resources:**
   ```bash
   # Check node resources
   kubectl top nodes
   
   # Check pod resource requests
   kubectl describe pod <pod-name> | grep -A 5 "Limits\|Requests"
   
   # Solution: Scale cluster or reduce resource requests
   ```

2. **Image Pull Errors:**
   ```bash
   # Check image pull secrets
   kubectl get secrets -n unified-ai-production
   
   # Verify image exists
   docker pull <registry>/unified-ai-api:v1.0.0
   
   # Solution: Fix image registry credentials or image path
   ```

3. **Configuration Errors:**
   ```bash
   # Validate configuration
   kubectl get configmap -n unified-ai-production
   kubectl get secrets -n unified-ai-production
   
   # Check environment variables
   kubectl exec <pod-name> -n unified-ai-production -- env
   ```

#### Database Connection Issues

**Symptoms:**
- Application cannot connect to database
- Connection timeout errors
- Authentication failures

**Diagnosis:**
```bash
# Test database connectivity from pod
kubectl run -it --rm debug --image=postgres:15 --restart=Never -- psql -h <db-host> -U postgres -d unified_ai

# Check database logs (RDS)
aws rds describe-db-log-files --db-instance-identifier unified-ai-db
aws rds download-db-log-file-portion --db-instance-identifier unified-ai-db --log-file-name error/postgresql.log.2024-01-15

# Test from application pod
kubectl exec -it <api-pod> -n unified-ai-production -- nc -zv <db-host> 5432
```

**Common Causes & Solutions:**

1. **Network Issues:**
   - Verify security groups allow traffic
   - Check VPC routing
   - Verify database is in same VPC or has proper peering

2. **Authentication Issues:**
   ```bash
   # Verify secrets
   kubectl get secret db-credentials -n unified-ai-production -o yaml
   
   # Test credentials
   psql -h <db-host> -U <username> -d unified_ai
   ```

3. **Database Overload:**
   ```bash
   # Check database connections
   psql -h <db-host> -U postgres -c "SELECT count(*) FROM pg_stat_activity;"
   
   # Check slow queries
   psql -h <db-host> -U postgres -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
   ```

#### High CPU/Memory Usage

**Symptoms:**
- Slow response times
- Pods being killed (OOMKilled)
- High resource utilization

**Diagnosis:**
```bash
# Check resource usage
kubectl top pods -n unified-ai-production
kubectl top nodes

# Check pod resource limits
kubectl describe pod <pod-name> -n unified-ai-production | grep -A 10 "Limits\|Requests"

# Check for OOM kills
kubectl get events -n unified-ai-production | grep OOMKilled
```

**Solutions:**

1. **Scale Horizontally:**
   ```bash
   # Scale deployment
   kubectl scale deployment unified-ai-api --replicas=5 -n unified-ai-production
   
   # Or enable autoscaling
   kubectl autoscale deployment unified-ai-api --min=3 --max=10 --cpu-percent=70 -n unified-ai-production
   ```

2. **Optimize Application:**
   - Review application logs for inefficient queries
   - Check for memory leaks
   - Optimize database queries

3. **Increase Resources:**
   ```yaml
   # Update deployment with higher limits
   resources:
     requests:
       cpu: 1000m
       memory: 2Gi
     limits:
       cpu: 4000m
       memory: 8Gi
   ```

#### SSL/TLS Certificate Issues

**Symptoms:**
- Certificate errors in browser
- HTTPS not working
- cert-manager errors

**Diagnosis:**
```bash
# Check certificate status
kubectl get certificates -n unified-ai-production
kubectl describe certificate unified-ai-tls -n unified-ai-production

# Check cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager

# Check certificate secret
kubectl get secret unified-ai-tls -n unified-ai-production
```

**Solutions:**

1. **Certificate Not Issued:**
   - Verify DNS records point to ingress
   - Check ClusterIssuer configuration
   - Verify Let's Encrypt rate limits

2. **Certificate Expired:**
   - cert-manager should auto-renew
   - Check renewal logs
   - Manually trigger renewal if needed

#### Ingress Not Routing Traffic

**Symptoms:**
- 404 errors
- Connection refused
- Wrong service responding

**Diagnosis:**
```bash
# Check ingress configuration
kubectl get ingress -n unified-ai-production
kubectl describe ingress unified-ai-ingress -n unified-ai-production

# Check ingress controller logs
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller

# Test from inside cluster
kubectl run -it --rm test --image=curlimages/curl --restart=Never -- curl -H "Host: app.unified-ai-assistant.com" http://unified-ai-web-service:80
```

**Solutions:**

1. **Verify Service Names:**
   - Ensure ingress backend service names match actual services
   - Check service ports match

2. **DNS Configuration:**
   - Verify DNS A records point to ingress IP
   - Check DNS propagation

### Performance Troubleshooting

#### Slow API Responses

**Check:**
- Database query performance
- Redis cache hit rates
- External API response times
- Network latency

**Tools:**
```bash
# Application performance monitoring
# Use APM tools (DataDog, New Relic, Elastic APM)

# Database slow query log
# Enable in PostgreSQL configuration

# Redis monitoring
redis-cli --latency
redis-cli INFO stats
```

### Logging & Debugging

#### View Application Logs

```bash
# Real-time logs
kubectl logs -f <pod-name> -n unified-ai-production

# Logs from all pods in deployment
kubectl logs -f deployment/unified-ai-api -n unified-ai-production

# Logs from previous container (if crashed)
kubectl logs <pod-name> -n unified-ai-production --previous

# Logs with timestamps
kubectl logs <pod-name> -n unified-ai-production --timestamps
```

#### Centralized Logging (ELK Stack)

```bash
# Access Kibana
kubectl port-forward -n logging svc/kibana 5601:5601
# Open http://localhost:5601

# Search logs in Elasticsearch
curl -X GET "elasticsearch:9200/_search?q=error" | jq
```

### Support Contacts

- **DevOps Team:** devops@unified-ai-assistant.com
- **On-Call:** +1-XXX-XXX-XXXX
- **Documentation:** docs.unified-ai-assistant.com
- **Emergency:** See on-call rotation schedule

### Additional Resources

- [Kubernetes Troubleshooting Guide](https://kubernetes.io/docs/tasks/debug/)
- [PostgreSQL Troubleshooting](https://www.postgresql.org/docs/current/logging.html)
- [NGINX Ingress Troubleshooting](https://kubernetes.github.io/ingress-nginx/troubleshooting/)

---

**Last Updated:** 2024  
**Version:** 1.0




