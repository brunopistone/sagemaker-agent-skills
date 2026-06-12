# HyperPod `hyp` CLI & SDK — practical reference

Self-contained reference for the **HyperPod CLI + SDK** so you can generate
working commands/code without leaving this skill. Read `hyperpod.md` first for
the big picture (when to use HyperPod, Slurm vs EKS, prerequisites).

> Scope: the `hyp` CLI manages HyperPod clusters orchestrated by **Amazon EKS /
> Kubernetes only**. Slurm clusters are NOT managed by `hyp` — use the console
> Quick setup, CloudFormation, or `aws sagemaker create-cluster` for Slurm.

## Install & basics

```bash
pip install sagemaker-hyperpod        # package: sagemaker-hyperpod (v3.8.0 at time of writing)
hyp --help                            # CLI binary is `hyp`; Python 3.8-3.11
```

Details (versions, class names, CLI nouns) describe v3.8.0 and may shift — always
confirm with `hyp --help` / `hyp <command> --help` and the public repo
`github.com/aws/sagemaker-hyperpod-cli` before relying on a specific flag.

## The five things `hyp` manages

| Domain                 | CLI noun(s)                         | SDK class             | Backed by                         |
| ---------------------- | ----------------------------------- | --------------------- | --------------------------------- |
| Training jobs          | `hyp-pytorch-job`, `hyp-recipe-job` | `HyperPodPytorchJob`  | EKS CRD (training operator)       |
| Inference (JumpStart)  | `hyp-jumpstart-endpoint`            | `HPJumpStartEndpoint` | EKS CRD → real SageMaker endpoint |
| Inference (custom)     | `hyp-custom-endpoint`               | `HPEndpoint`          | EKS CRD → real SageMaker endpoint |
| Cluster infrastructure | `cluster-stack`, `cluster`          | `HpClusterStack`      | CloudFormation + Helm             |
| Dev spaces (Jupyter)   | `hyp-space*`                        | `HPSpace`             | EKS CRD                           |

The CLI uses a **schema-driven** design: most `hyp create ...` flags are generated
from the config schema for that domain, so the exact flag set depends on the
installed template version. `hyp <noun> --help` is authoritative.

## Connect to a cluster

```bash
hyp list-cluster [--region us-west-2] [--output TABLE|JSON]
hyp set-cluster-context --cluster-name <eks-backed-cluster>   # points kubeconfig at it
hyp get-cluster-context
hyp get-monitoring                                            # observability addon config
```

## Create cluster infrastructure (EKS)

Cluster creation goes through the **init → create** flow (there is no standalone
`create cluster-stack` command):

```bash
hyp init cluster-stack        # scaffold a config from the template
# edit the generated config (VPC, EKS cluster name, instance groups, Helm operators...)
hyp create                    # provisions via CloudFormation + installs the Helm chart
hyp list cluster-stack [--region ...] [--status ...]
hyp describe cluster-stack --stack-name <n>
hyp update cluster ...
hyp delete cluster-stack --stack-name <n> [--retain-resources ...]
```

SDK equivalent:

```python
from sagemaker.hyperpod.cluster_management.hp_cluster_stack import HpClusterStack

stack = HpClusterStack(resource_name_prefix="demo", ...)   # many infra fields
stack.create(region="us-west-2")
print(stack.get_status())
HpClusterStack.list(region="us-west-2")
HpClusterStack.delete("HyperpodClusterStack-abcde", region="us-west-2")
```

Stack creation installs an umbrella **Helm chart** with operators for training,
inference, health monitoring, job auto-restart, GPU/Neuron/EFA device plugins,
MPI, MLflow, and more — this is what makes a HyperPod EKS cluster "ready to train".

## Two ways to run training on HyperPod-EKS

There are **two distinct ways** to launch training on a HyperPod EKS cluster —
pick one:

1. **The `hyp` CLI / SDK** (below) — AWS's abstraction; generates the CRD for you
   and adds logs/exec/quota helpers. Easiest if you have `hyp` set up.
2. **Raw `kubectl` + a Kubeflow `PyTorchJob`** (see "Train via kubectl" below) —
   you write a pod manifest and `kubectl apply` it. This is what several AWS
   workshops use; lower-level but no `hyp` dependency.

Both ultimately run a training operator on the cluster. Use whichever matches the
user's tooling; don't imply `hyp` is the only option.

## Run a training job — via `hyp`

```bash
hyp create hyp-pytorch-job \
  --job-name my-job --image <ecr-image> \
  --instance-type ml.g5.8xlarge \
  --replica-count 2 --tasks-per-node 8 \
  --namespace my-ns

hyp list hyp-pytorch-job -n my-ns
hyp describe hyp-pytorch-job --job-name my-job -n my-ns
hyp list-pods hyp-pytorch-job --job-name my-job -n my-ns
hyp get-logs  hyp-pytorch-job --job-name my-job --pod-name <pod> -n my-ns
hyp get-operator-logs hyp-pytorch-job --since-hours 1
hyp exec hyp-pytorch-job --job-name my-job --all-pods -- nvidia-smi
hyp delete hyp-pytorch-job --job-name my-job -n my-ns
```

Notes:

- **`--instance-type` is required when you request accelerators (GPU/Neuron).**
- Use **`--replica-count`** (the newer field); `--node-count` is deprecated.
- `hyp-recipe-job` is the recipe-driven variant of the same job (see below).

SDK equivalent:

```python
from sagemaker.hyperpod.training.hyperpod_pytorch_job import HyperPodPytorchJob
from sagemaker.hyperpod.common.config import Metadata

job = HyperPodPytorchJob(
    metadata=Metadata(name="my-job", namespace="my-ns"),
    replicaSpecs=[...],     # containers, resources, nodeSelector
    runPolicy=...,          # cleanPodPolicy, ttlSecondsAfterFinished
)
job.create()

job = HyperPodPytorchJob.get("my-job", namespace="my-ns")
job.refresh(); print(job.status.conditions)
for p in job.list_pods():
    print(job.get_logs_from_pod(p))
job.delete()
```

## Run a recipe job

`hyp-recipe-job` uses the same job machinery driven by a curated recipe (from the
public `github.com/aws/sagemaker-hyperpod-recipes` project — NeMo-based). Use it
to fine-tune/pretrain a supported model without hand-writing the training config.

```bash
hyp init hyp-recipe-job      # scaffold; pick a recipe + cluster settings
hyp create hyp-recipe-job ...
```

## Train via kubectl (Kubeflow PyTorchJob) — the no-`hyp` path

If you'd rather not use `hyp`, launch training by applying a **Kubeflow
`PyTorchJob`** manifest with `kubectl`. This is the pattern in several AWS
workshops: a pod runs `torchrun` over your `train.py`, reading data/writing the
model on a mounted **FSx for Lustre** volume.

```yaml
# pod-finetuning.yaml
apiVersion: "kubeflow.org/v1"
kind: PyTorchJob                      # the Kubeflow CRD (NOT HyperPodPyTorchJob)
metadata:
  name: qwen3-4b-sft
spec:
  elasticPolicy:
    rdzvBackend: c10d
    minReplicas: 1
    maxReplicas: 1
    maxRestarts: 3
  pytorchReplicaSpecs:
    Worker:
      replicas: 1
      restartPolicy: OnFailure
      template:
        spec:
          volumes:
            - name: fsx-volume
              persistentVolumeClaim:
                claimName: fsx-claim          # an FSx for Lustre PVC
          containers:
            - name: pytorch
              image: 763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-training:2.8.0-gpu-py312-cu129-ubuntu22.04-ec2
              resources:
                requests: { nvidia.com/gpu: 4 }
                limits:   { nvidia.com/gpu: 4 }
              command:
                - /bin/bash
                - -c
                - |
                  pip install --no-cache-dir -r /data/shared/<job>/requirements.txt && \
                  torchrun --nnodes=1 --nproc_per_node=4 \
                    --rdzv_backend=c10d --rdzv_endpoint=${PET_RDZV_ENDPOINT} \
                    --rdzv_id=qwen3-4b-sft --max_restarts=3 \
                    /data/shared/<job>/scripts/train.py \
                    --config /data/shared/<job>/args.yaml
              volumeMounts:
                - { name: fsx-volume, mountPath: /data }
```

```bash
kubectl apply -f pod-finetuning.yaml
kubectl get pytorchjob qwen3-4b-sft
kubectl logs -f qwen3-4b-sft-worker-0
```

- The training **operator must be installed** on the cluster (the HyperPod EKS
  Helm chart includes training operators). `train.py` here is an ordinary
  transformers/TRL/PEFT FSDP script reading from the FSx mount.
- An `args.yaml` carries the training config (model id, FSx data/output paths,
  `fsdp` settings); a separate `deployment.yaml` (kind `InferenceEndpointConfig`,
  `inference.sagemaker.aws.amazon.com/v1alpha1`) deploys the result with a vLLM
  image — that's the HyperPod **inference operator**, distinct from the `hyp`
  endpoint commands above.

Exact CRD apiVersions, image tags, and operator availability are version- and
cluster-specific — confirm against your cluster and current AWS workshop/docs.

## Deploy & invoke inference

```bash
# JumpStart model -> endpoint
hyp create hyp-jumpstart-endpoint --model-id <id> --instance-type ml.g5.8xlarge --endpoint-name my-js

# Custom model (source: s3 | fsx | huggingface | kubernetesVolume)
hyp create hyp-custom-endpoint --endpoint-name my-cust --instance-type ml.g5.8xlarge \
  --model-source-type s3 --s3-bucket-name <b> --s3-region us-west-2 --image-uri <ecr> ...

hyp list     hyp-jumpstart-endpoint -n default
hyp describe hyp-custom-endpoint --name my-cust [--full]
hyp invoke   hyp-custom-endpoint --endpoint-name my-cust --body '{"inputs":"hello"}'
hyp delete   hyp-jumpstart-endpoint --name my-js
```

- The HyperPod inference operator turns the CRD into a **real SageMaker endpoint**;
  `hyp invoke` errors clearly if the endpoint isn't `InService` yet.
- `--body` must be valid JSON. Custom endpoints support autoscaling driven by a
  CloudWatch metric (target value, metric name/stat, dimensions).

SDK equivalent:

```python
from sagemaker.hyperpod.inference.hp_jumpstart_endpoint import HPJumpStartEndpoint
from sagemaker.hyperpod.inference.hp_endpoint import HPEndpoint

ep = HPJumpStartEndpoint(...)   # model_id, model_version, accept_eula, instance_type
ep.create(debug=True)

one = HPEndpoint.model_construct().get("my-cust", "default")
one.delete()
```

## Dev spaces (optional)

`hyp hyp-space*` commands manage interactive Jupyter dev spaces on the cluster
(`start`/`stop`/`portforward`/`space-access`). Useful for interactive
development against cluster resources; not required for batch training/inference.

## Cost & cleanup (repeat for users)

- A HyperPod cluster bills **while it's running**, idle or not — delete it when
  done (`hyp delete cluster-stack ...`, the console, or `aws sagemaker delete-cluster`).
- Endpoints created on the cluster keep billing — `hyp delete hyp-*-endpoint ...`.
- Jobs only consume cluster capacity while running, but the cluster underneath
  still bills regardless.

## Public references (safe to share)

- CLI/SDK repo: https://github.com/aws/sagemaker-hyperpod-cli
- Recipes repo: https://github.com/aws/sagemaker-hyperpod-recipes
- HyperPod + EKS docs: https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-eks.html
