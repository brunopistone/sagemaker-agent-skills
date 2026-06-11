# SageMaker HyperPod (clusters, recipes, the `hyp` CLI)

HyperPod is a **persistent, resilient training cluster** you provision and keep
running, submitting many jobs against it (with auto-detect/replace of failed
nodes and auto-resume). Contrast with SageMaker AI managed jobs, which are
ephemeral and zero-ops. Steer newcomers here only when scale/duration/resiliency
justify it (see `decision-guide.md`).

> All resources below are PUBLIC AWS docs/repos — safe to share with anyone.

## Orchestrator: Slurm vs EKS (chosen at cluster creation)

- **Slurm** — HPC-style (`sbatch`/`squeue`/`srun`). VPC optional (platform-managed
  by default). The console **Quick setup** auto-creates VPC, subnets, security
  groups, S3 bucket, IAM role, and FSx for Lustre — the lowest-friction first
  cluster.
- **Amazon EKS** — Kubernetes-style (`kubectl`, pods). VPC mandatory. The newest
  tooling (the `hyp` CLI, the HyperPod SDK, inference, Spaces) targets EKS first.

Newcomer guidance: want the simplest first cluster → **Slurm Quick setup**;
planning to grow into containerized training + inference / want the `hyp` CLI →
**EKS**.

## Ways to create a cluster

1. **AWS Console** → SageMaker AI → HyperPod Clusters → Create → choose Slurm or
   EKS → Quick setup. Best for a newcomer's first cluster.
2. **CloudFormation** templates (public `aws-samples/awsome-distributed-training`).
3. **boto3 / AWS CLI**: `aws sagemaker create-cluster` (`CreateCluster` API;
   related `DescribeCluster`, `ListClusters`, `UpdateCluster`, `DeleteCluster`).
4. **HyperPod CLI** (`hyp`) — see below; targets EKS-orchestrated clusters.

## The HyperPod CLI (`hyp`) — EKS only

- Install: `pip install sagemaker-hyperpod` (package `sagemaker-hyperpod`,
  v3.8.0 at time of writing; Python 3.8-3.11). The command is **`hyp`**.
- **`hyp` manages EKS-orchestrated clusters only.** For a **Slurm** cluster, use
  the console Quick setup, CloudFormation, or `aws sagemaker create-cluster` —
  not `hyp`.
- Cluster creation goes through an **init → create** flow:
  `hyp init cluster-stack` → edit the generated config → `hyp create`
  (there is no standalone `create cluster-stack` command). Then
  `hyp set-cluster-context` / `hyp list-cluster`.
- Training jobs: `hyp create hyp-pytorch-job ...` (note: prefer `--replica-count`;
  `--node-count` is deprecated). Watch with `hyp list-pods` / `hyp get-logs`.
- Recipe jobs: `hyp create hyp-recipe-job ...`.
- Inference: `hyp create hyp-jumpstart-endpoint` or `hyp-custom-endpoint`, then
  `hyp invoke`.

There is also a matching Python SDK (objects like `HyperPodPytorchJob`,
`HPJumpStartEndpoint`, `HpClusterStack`). For the full command/SDK walkthrough
with examples, read **`hyperpod-cli-reference.md`**. Command/arg details evolve
across versions — confirm against `hyp --help` and the public CLI repo (link
below) rather than asserting exact flags from memory.

## Recipes (pre-built training configs)

The public **`aws/sagemaker-hyperpod-recipes`** repo holds YAML recipes for
pretraining/fine-tuning popular open models, runnable on HyperPod-EKS,
HyperPod-Slurm, **or** SageMaker AI managed training jobs.

- Models commonly covered: Amazon **Nova**, **Llama** (3.x/4), **Qwen**,
  **DeepSeek-R1 distilled**, **Gemma**, and others. The exact list changes —
  check the repo's current `recipes_collection/` for what's available now.
- Techniques: continued pretraining, SFT (full / LoRA / QLoRA), DPO, and RL
  variants (availability varies by model).
- Launch flows: edit the recipe + cluster config and run the repo's launcher
  scripts (Slurm or k8s), or launch via the SDK
  (`ModelTrainer.from_recipe(...)` for a managed job — see `llm-finetuning.md`
  Option B).

## Prerequisites (in addition to `prerequisites.md`)

- **HyperPod execution role** (distinct from the per-job role).
- **Cluster-level quotas** (Service Quotas → Amazon SageMaker): instances per
  cluster, instances across clusters, and per-instance _"ml.\<type\> for **cluster**
  usage"_ (note: cluster usage, separate from training-job usage).
- **VPC**: mandatory for EKS, optional for Slurm (Quick setup can auto-create).
- **S3 bucket** for lifecycle scripts; optionally **FSx for Lustre** for a fast
  shared filesystem (same AZ as compute).
- **Lifecycle scripts** to provision nodes (Quick setup generates defaults).

## Cost & cleanup

A HyperPod cluster bills **for as long as it's running**, regardless of whether a
job is active. Tell users to delete/stop the cluster when idle (`aws sagemaker
delete-cluster ...`, the console, or `hyp` delete commands) and to delete any
inference endpoints they created on it.

## Public references (safe to share)

- Docs landing: https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod.html
- Quickstart: https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-quickstart.html
- Prerequisites: https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-prerequisites.html
- Recipes doc: https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-recipes.html
- Recipes repo: https://github.com/aws/sagemaker-hyperpod-recipes
- CLI repo: https://github.com/aws/sagemaker-hyperpod-cli
- Distributed-training samples: https://github.com/aws-samples/awsome-distributed-training
- Slurm workshop: https://catalog.workshops.aws/sagemaker-hyperpod/en-US
- EKS workshop: https://catalog.workshops.aws/sagemaker-hyperpod-eks/en-US
