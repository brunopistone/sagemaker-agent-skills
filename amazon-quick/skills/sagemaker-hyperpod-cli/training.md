# Training: PyTorch Jobs & Recipe Jobs

**SDK class:** `HyperPodPytorchJob` — `src/sagemaker/hyperpod/training/hyperpod_pytorch_job.py`
**CLI nouns:** `hyp-pytorch-job` (and `hyp-recipe-job`, the recipe-driven variant)
**Backed by:** Kubernetes CRD `HyperPodPyTorchJob`, group `sagemaker.amazonaws.com`, version `v1`, plural `hyperpodpytorchjobs`. The training operator runs in namespace `aws-hyperpod` (label `hp-training-control-plane`).

`HyperPodPytorchJob` subclasses `_HyperPodPytorchJob` (the unified Pydantic config in `training/config/hyperpod_pytorch_job_unified_config.py`) and adds `metadata: Metadata` and `status: HyperPodPytorchJobStatus`.

## SDK Methods

| Method | Kind | Notes |
|--------|------|-------|
| `create(debug=False)` | instance | Builds the CRD body and POSTs via `CustomObjectsApi.create_namespaced_custom_object` |
| `list(namespace=None)` | classmethod | → `List[HyperPodPytorchJob]`; defaults to current-context namespace |
| `get(name, namespace=None)` | classmethod | → one job |
| `delete()` | instance | Also deletes the `training-config-<name>` ConfigMap (recipe jobs) |
| `refresh()` | instance | Re-fetches `.status` |
| `list_pods()` | instance | Pods labeled `HPJob=<name>` |
| `get_logs_from_pod(pod_name, container=None)` | instance | Defaults to first container |
| `get_operator_logs(since_hours)` | classmethod | Logs from the training operator pod |
| `exec_command(command, pod=None, all_pods=False, container=None)` | instance | `kubectl exec` equivalent |

Module-level helper `list_accelerator_partition_types(instance_type)` returns the MIG partition types actually allocatable on cluster nodes of that instance type (queries `nvidia.com/<profile>` on node `status.allocatable`).

`verify_kube_config()` lazily loads kubeconfig once (class var `is_kubeconfig_loaded`) and checks Kubernetes version compatibility.

## Resource & Accelerator Handling

`create()` calls `allocate_quotas_if_applicable()` → `_process_replica_resources()`, which reads the first replica's container resources and applies HyperPod **task-governance / quota allocation** logic from `training/quota_allocation_util.py`. Key rules:

- Resource keys recognized: `cpu`/`vcpu`, `memory`, `accelerators` (or raw `nvidia.com/gpu` / `aws.amazon.com/neuron`), and `aws.amazon.com/efa`. Labels are in `cli/constants/command_constants.py` (`NVIDIA_GPU_RESOURCE_LIMIT_KEY`, `NEURON_RESOURCE_LIMIT_KEY`, `EFA_RESOURCE_LIMIT_KEY`, `INSTANCE_TYPE_LABEL`).
- **`--instance-type` is required when accelerator resources are requested** (raises `ValueError` otherwise).
- Accelerator partitions (MIG) handled via `accelerator_partition_util.py` + `INSTANCE_TYPE_MIG_PROFILES` / `INSTANCE_RESOURCES` in `training/constants.py`.
- Default replica count is `1` if unset/zero.
- `node_count` is the older field; **`replica_count` is preferred** (`node_count` deprecated as of v3.8.0).

## CLI Usage

```bash
# Flags below are GENERATED from hyperpod_pytorch_job_template schema (see templates-and-init.md).
hyp create hyp-pytorch-job \
  --job-name my-job --image <ecr-image> \
  --instance-type ml.g5.8xlarge \
  --node-count 2 --tasks-per-node 8 \
  --namespace my-ns

hyp list hyp-pytorch-job -n my-ns
hyp describe hyp-pytorch-job --job-name my-job -n my-ns
hyp list-pods hyp-pytorch-job --job-name my-job -n my-ns
hyp get-logs hyp-pytorch-job --job-name my-job --pod-name <pod> -n my-ns
hyp get-operator-logs hyp-pytorch-job --since-hours 1
hyp exec hyp-pytorch-job --job-name my-job --all-pods -- nvidia-smi   # or -p <pod>
hyp delete hyp-pytorch-job --job-name my-job -n my-ns
hyp list-accelerator-partition-type --instance-type ml.p4d.24xlarge
```
`hyp create hyp-pytorch-job` is `training.py::pytorch_create`, which calls `job.create(debug=debug)` where `job` is the domain object produced by `@generate_click_command`.

## SDK Usage

```python
from sagemaker.hyperpod.training.hyperpod_pytorch_job import HyperPodPytorchJob
from sagemaker.hyperpod.common.config import Metadata
# build replicaSpecs/runPolicy via the unified config models, or via the template flat model's to_domain()

job = HyperPodPytorchJob(
    metadata=Metadata(name="my-job", namespace="my-ns"),
    replicaSpecs=[...],          # ReplicaSpec list (containers, resources, nodeSelector)
    runPolicy=...,               # cleanPodPolicy, ttlSecondsAfterFinished
)
job.create()

jobs = HyperPodPytorchJob.list(namespace="my-ns")
job = HyperPodPytorchJob.get("my-job", namespace="my-ns")
job.refresh(); print(job.status.conditions)
for p in job.list_pods():
    print(job.get_logs_from_pod(p))
job.delete()
```

## Recipe Jobs (`hyp-recipe-job`)

Same SDK class and CRD; the recipe variant is driven by the **sagemaker-hyperpod-recipes** submodule (NeMo recipes, branch `release-1.3.3`). CLI commands are `copy.copy()` of the pytorch-job commands. `hyp init hyp-recipe-job` uses a `"dynamic"` template type (no fixed schema package — see `init_constants.py::TEMPLATES["hyp-recipe-job"]`).
