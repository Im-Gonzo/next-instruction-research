# Builder kit — Experiment 3 (identical across all three conditions)

You are a **builder**. You will be given a description of a software architecture in one
form (a raw talk transcript, a prose summary, or a compact kernel notation). Reconstruct
its **component graph** and return it as JSON — nothing else.

## Output schema (return ONLY this)
```json
{"nodes": ["id", ...], "edges": [["from_id","to_id"], ...]}
```
Rules:
- Use **only** ids from the component vocabulary below.
- Put an id in `"nodes"` **only if the architecture actually contains that component**.
- **Some listed components are not part of this architecture — leave those out.**
- Each edge is a directed `["from","to"]` pair using ids you included. Direction = the way
  a request, data, config, or provisioning action flows.

## Component vocabulary (id — what it is)
```
acm          — AWS Certificate Manager (TLS certificates)
alb          — application load balancer (L7)
ami          — machine image (baked server image)
apigateway   — API Gateway
asg          — EC2 autoscaling group
auth_sc      — authentication sidecar
authz_sc     — authorization sidecar
backend      — a generic backend web service
bitbucket    — Bitbucket (Atlassian product)
cfn          — CloudFormation template (infrastructure-as-code)
client       — a developer / tenant
clusters     — Envoy CDS cluster configuration
cloudfront   — CloudFront CDN distribution
confluence   — Confluence (Atlassian product)
consul       — Consul service mesh
context      — rendered service context
customer     — an end user
dynamo       — DynamoDB table
ec2          — EC2 compute instances
eks          — EKS / Kubernetes cluster
envoy        — Envoy proxy fleet
igw          — internet gateway
iamrole      — IAM role
jira         — Jira (Atlassian product)
keypair      — EC2 key pair
kinesis      — Kinesis stream
lambda       — AWS Lambda function
listeners    — Envoy LDS listener configuration
nginx        — NGINX proxy
nlb          — network load balancer (L4)
osb          — Open Service Broker API service
packer       — Packer image builder
parameters   — CloudFormation template parameters
rds          — RDS relational database
redis        — Redis cache
rl_sc        — rate-limit sidecar
route53      — Route 53 DNS
routes       — Envoy RDS route configuration
s3           — S3 bucket
salt         — SaltStack configuration management
sg           — security group
sovereign    — an Envoy control-plane service
sqs          — SQS queue
statuspage   — Status Page (Atlassian product)
subnet       — VPC subnet
templates    — configuration templates
terraform    — Terraform IaC
vpc          — virtual private cloud
worker       — an async provisioning worker
```
(49 entries; not all are present in the system you'll be given.)
