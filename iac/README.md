# Part 3 – Infrastructure as Code (Terraform, AWS)

This folder contains Terraform code to deploy the **eGain Knowledge Indexing Service** on AWS using:
- **ECS Fargate** (container runtime)
- **Application Load Balancer (ALB)**
- **API Gateway (HTTP API)** in front of ALB
- **RDS MySQL** (included to satisfy the requirement for an RDS/DynamoDB configuration; the assignment app can still use SQLite)
- **IAM** roles/policies for ECS tasks
- **CloudWatch** log group + basic alarms
- **Blue/Green** deployment strategy using **ECS + CodeDeploy** (deployment controller)

> Note: The assignment implementation uses SQLite by default. This IaC shows how I would deploy the service on AWS and where
> RDS/MySQL fits in a production mapping.

---

## Prerequisites

- AWS account with permissions to create VPC/ECS/ALB/APIGW/RDS/IAM/CloudWatch resources
- AWS CLI configured (`aws configure`) with a default region
- Terraform >= 1.6
- Docker (to build/push the container image)
- (Recommended) An S3 + DynamoDB backend for Terraform state locking (not included here to keep setup simple)

---

## What gets created

- VPC with public subnets (2 AZs)
- ECS Cluster + Fargate Service (2 tasks by default)
- ALB with two target groups (blue/green)
- CodeDeploy application + deployment group for ECS blue/green
- API Gateway HTTP API that proxies to the ALB
- CloudWatch log group for the service
- CloudWatch alarms (CPU, memory, ALB 5xx, RDS CPU)

---

## Deployment instructions

### 1) Build and push the image to ECR

Terraform creates an ECR repository. After `terraform apply`, you’ll see an output called `ecr_repository_url`.

```bash
# from the repo root where your Dockerfile lives:
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account_id>.dkr.ecr.<region>.amazonaws.com

docker build -t egain-knowledge-service:latest .
docker tag egain-knowledge-service:latest <ecr_repository_url>:latest
docker push <ecr_repository_url>:latest
```

### 2) Deploy infrastructure

```bash
cd egain_part3_iac/terraform
terraform init
terraform apply
```

### 3) Verify

Terraform outputs:
- `api_gateway_invoke_url`  (your public endpoint)
- `alb_dns_name`

Test:

```bash
curl -s <api_gateway_invoke_url>/api/v1/health
```

---

## Scaling strategy

- **ECS Service autoscaling**: configured to scale task count based on CPU and memory utilization.
- **ALB**: spreads traffic across tasks; can add request-based scaling if desired.
- **RDS**: start with a small instance for dev; in production use Multi-AZ + read replicas and scale instance class/storage as needed.

---

## Blue/Green deployments

This setup uses **ECS + CodeDeploy**:
- Two target groups: **blue** (current) and **green** (new)
- CodeDeploy shifts traffic gradually (canary/linear) and can rollback on CloudWatch alarms

To deploy a new version:
- Push a new image tag to ECR
- Update `var.image_tag` (or use CI to update task definition)
- `terraform apply` (or a pipeline triggers a CodeDeploy deployment)

---

## Configuration

Key variables (see `variables.tf`):
- `project_name`
- `aws_region`
- `image_tag`
- `desired_count`
- `task_cpu`, `task_memory`
- `api_keys_json` (passed to the container as `API_KEYS_JSON`)
- `db_path` (defaults to file-backed SQLite inside the container; for durable storage you’d mount EFS)
