# Prerequisites (walk through these before running anything)

A newcomer with perfect code but no IAM role / bucket / quota will hit a runtime
error. Confirm each item below. Offer to generate the setup commands; never
assume they exist. Suggest running interactive AWS auth via `! <command>` in the
session if they need to log in (e.g. `! aws sso login`).

## Common to all SageMaker AI workloads

1. **AWS account + credentials.** `aws sts get-caller-identity` should return an
   identity. If not, they need to configure the AWS CLI (`aws configure`) or SSO.
2. **Region.** Pick one with the GPU capacity they need (e.g. `us-west-2`,
   `us-east-1`). All resources (bucket, role, job) should share a region.
3. **Execution role (IAM).** SageMaker assumes a role to access S3, ECR, logs.
   - In **SageMaker Studio**, a role already exists — `get_execution_role()` returns it.
   - **Locally**, they must pass a role ARN with the `AmazonSageMakerFullAccess`
     managed policy (for getting started) and S3 access to their bucket.
4. **S3 bucket.** Holds input data, code, and output artifacts. The SDK can use a
   default bucket (`Session().default_bucket()`) or a named one. Confirm it's in
   the same region.
5. **Service quota for the instance type.** This is the #1 newcomer blocker. GPU
   instances (ml.g5, ml.g6, ml.p4d, ml.p5...) often start at quota 0. Check &
   request in the **Service Quotas console → Amazon SageMaker**, e.g.
   _"ml.g5.12xlarge for training job usage"_. Quota increases can take time —
   warn them early.
6. **Model access (for gated models).** Llama/Mistral/etc. on HuggingFace need a
   HF account + accepted license + an `HF_TOKEN`. JumpStart models may need EULA
   acceptance.

### Minimal local setup commands (offer, don't auto-run)

```bash
# 1. Verify identity & region
aws sts get-caller-identity
aws configure get region

# 2. Create a bucket (skip if using the SDK default)
aws s3 mb s3://my-sagemaker-getting-started-<unique> --region us-west-2

# 3. (If no role yet) the simplest getting-started execution role:
#    create a role trusted by sagemaker.amazonaws.com with AmazonSageMakerFullAccess.
#    Prefer the Console "Create role" wizard for newcomers; scope down later.
```

Check quota & GPU sizing with `sizing.md` so you request the right instance the
first time (quota increases can take hours-to-days — do this early).

## Additional prerequisites for HyperPod

See `hyperpod.md` for the full flow. Beyond the above:

- **HyperPod execution role** (distinct from the job role).
- **Cluster-level quotas**: "instances per HyperPod cluster", "instances across
  clusters", and per-instance "_ml.\<type\> for cluster usage_" (note: _cluster_
  usage, different from _training job_ usage).
- **VPC**: mandatory for EKS, optional for Slurm (Quick setup can auto-create).
- **S3 bucket** for lifecycle scripts; optionally **FSx for Lustre** for a fast
  shared filesystem.
- **Lifecycle scripts** to provision nodes (Quick setup generates defaults).

## Cost & cleanup reminder (always state this)

- GPU instances and live endpoints bill **per second while they exist**, used or not.
- After a managed job: artifacts sit in S3 (cheap); nothing keeps running.
- After deploying an endpoint: **it keeps billing until deleted** —
  `endpoint.delete()` / delete the endpoint, config, and model.
- A HyperPod cluster bills **as long as it's running** — stop/delete it when idle.
