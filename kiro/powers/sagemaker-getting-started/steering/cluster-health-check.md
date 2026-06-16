# Pre-flight cluster health check (before an expensive training run)

Goal: **before** launching a costly multi-GPU / multi-node training job, run a
quick validation job that confirms the cluster is actually healthy — GPUs,
network fabric (EFA), and inter-GPU communication (NCCL) all working. A failed
8-GPU job can waste hours and hundreds of dollars; these checks catch the common
causes in minutes.

Use this when: commissioning a new cluster config, before a big/long distributed
run, after infra changes, or to troubleshoot a training failure. Skip it for a
trivial single-GPU job.

## What it validates

- **GPU health** — memory, temperature/thermal throttling, power, driver version, utilization
- **System resources** — CPU, RAM, disk
- **Network fabric** — EFA (Elastic Fabric Adapter) detection + provider validation
- **NCCL communication** — all-reduce / all-gather bandwidth across GPUs and nodes (test size scales with cluster size)
- **DCGM diagnostics** — PCIe, GPU memory integrity, targeted stress tests
- **Cluster topology** — world size, node count, GPUs/node; inter- vs intra-node patterns
- **Reporting** — overall PASS / WARN / FAIL with recommendations; metrics written to S3 and CloudWatch (and MLflow)

## Reference implementation (public repo)

A ready-to-use implementation is the public repo
**`github.com/brunopistone/sagemaker-training-jobs-cluster-health-check`**. It
packages the checks into a container and launches them as a SageMaker Training
job with the SDK V3 `ModelTrainer`. Shape of it:

- `container/` — `Dockerfile` + `create-image.sh` to build/push the health-check
  image to ECR.
- `scripts/train.py` (Torchrun) and `scripts/train_mpi.py` (MPI) — the checks.
- `notebook_torchrun.ipynb` / `notebook_mpi.ipynb` — launch the job.
- Output: `s3://<bucket>/<job-name>/metrics/health_check_metrics.json`.

## Launch pattern (SDK V3)

Same `ModelTrainer` flow as ordinary training (see `llm-finetuning.md` Option 2),
pointed at the health-check container and your cluster's networking:

```python
from sagemaker.train.model_trainer import ModelTrainer
from sagemaker.train.configs import Compute, Networking
from sagemaker.train.distributed import Torchrun   # or: from sagemaker.train.distributed import MPI

model_trainer = ModelTrainer(
    training_image="<health-check-image-in-ECR>",
    compute=Compute(instance_type="ml.g5.12xlarge", instance_count=2),
    networking=Networking(                       # required for multi-node EFA checks
        subnet_ids=["subnet-xxxxxxxx"],
        security_group_ids=["sg-xxxxxxxx"],
    ),
    distributed=Torchrun(),                      # or MPI(process_count_per_node=<NUM_GPUS>)
    # ... role, output, etc.
)
model_trainer.train(wait=True)
```

When to use the distributed flag:
- **Multi-node** → `Torchrun()` **required** (validates inter-node comms).
- **Single-node multi-GPU** → `Torchrun()` / `MPI(...)` recommended (tests NCCL across GPUs).
- **Single GPU** → omit `distributed=...`; basic health checks only.

## Why it matters for the user

- Catches EFA misconfiguration, NCCL bandwidth problems, thermal/driver/memory
  issues **before** they silently stall or crash a long training run.
- Cheap insurance: a few minutes on a validation job vs. hours of wasted GPU time.
- Good fit as a CI/MLOps pre-step before kicking off distributed training, and a
  natural companion to the distributed-training and HyperPod paths.

> The repo's exact container contents and check thresholds evolve — read its
> `README.md` and scripts for current specifics, and confirm `Networking` /
> distributed arguments against your installed `sagemaker` version.
