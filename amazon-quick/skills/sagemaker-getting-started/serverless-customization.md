# Serverless model customization (easiest fine-tuning path)

Goal: fine-tune a base model **without choosing an instance, sizing GPUs, or
writing a training script**. SageMaker runs the customization on **serverless
training jobs** — you supply a base model, a dataset, and a technique; the
service picks and manages the compute. This is the gentlest on-ramp for a
newcomer who just wants a customized model.

Prefer this over the self-managed training-job path (`llm-finetuning.md`) or
HyperPod whenever the base model and technique are supported here — there is no
hardware to size or quota to request.

## When to use it vs. the other paths

| Path | You manage | Use when |
|---|---|---|
| **Serverless customization (this file)** | nothing — just data + technique | supported base model (e.g. Llama, Nova, common OSS); you want zero infra |
| Training job (`llm-finetuning.md`) | instance type, script/container | custom training logic, an unsupported model, or full control |
| HyperPod (`hyperpod.md`) | a persistent cluster | very large/long runs needing resiliency |

## Supported techniques

- **SFT** — supervised fine-tuning on prompt/response data
- **DPO** — direct preference optimization (chosen/rejected pairs)
- **RLVR** — RL from verifiable rewards (needs a reward function, registered as a SageMaker Hub Evaluator ARN)
- **RLAIF** — RL from AI feedback (built-in or custom judge prompt)
- Nova models additionally support CPT/RFT variants

## What you need first

1. **A base model name as it appears on SageMaker Hub** (e.g.
   `meta-textgeneration-llama-3-8b`). The Hub name can differ from the common
   name — use the exact Hub identifier.
2. **A training dataset in S3**, in the region you'll run in.
3. **An execution role** (`get_execution_role()` in Studio, or a role ARN).
4. **EULA acceptance for gated models** (Meta/Llama require explicitly accepting
   the license — see below).

## Install

```bash
pip install "sagemaker>=3.7.1,<4.0" boto3
```

## SFT example (the canonical serverless pattern)

```python
import boto3
from botocore.exceptions import ClientError
from sagemaker.core.helper.session_helper import Session, get_execution_role
from sagemaker.core.resources import ModelPackageGroup
from sagemaker.ai_registry.dataset import DataSet
from sagemaker.train.sft_trainer import SFTTrainer
from sagemaker.train.common import TrainingType

sm_client = boto3.Session().client("sagemaker")
sagemaker_session = Session(sagemaker_client=sm_client)
bucket = sagemaker_session.default_bucket()

BASE_MODEL = "meta-textgeneration-llama-3-8b"   # exact SageMaker Hub name
TRAINING_DATA_S3 = "s3://my-bucket/data/train/"
S3_OUTPUT_PATH = f"s3://{bucket}/finetuning-output/"
ROLE_ARN = get_execution_role()
MODEL_PACKAGE_GROUP_NAME = "my-use-case-v1"     # lowercase, hyphens, 1-63 chars
ACCEPT_EULA = False                              # set True ONLY after accepting the license

# 1. Register a model package group (idempotent) + dataset in the AI Registry
try:
    model_package_group = ModelPackageGroup.create(
        model_package_group_name=MODEL_PACKAGE_GROUP_NAME,
        model_package_group_description="",
    )
except ClientError as e:
    if e.response["Error"]["Code"] in ("ResourceInUse", "ValidationException"):
        model_package_group = ModelPackageGroup.get(
            model_package_group_name=MODEL_PACKAGE_GROUP_NAME)
    else:
        raise

dataset = DataSet.create(name=MODEL_PACKAGE_GROUP_NAME, source=TRAINING_DATA_S3, wait=True)

# 2. Configure the trainer — note: NO instance type, NO container, NO compute config
trainer = SFTTrainer(
    model=BASE_MODEL,
    training_type=TrainingType.LORA,             # or full fine-tuning
    model_package_group=model_package_group,
    training_dataset=dataset.arn,                # a registered DataSet ARN, not a raw S3 path
    s3_output_path=S3_OUTPUT_PATH,
    sagemaker_session=sagemaker_session,
    # accept_eula=ACCEPT_EULA,                    # uncomment for Meta/Llama models
    role=ROLE_ARN,
)

# Hyperparameters are auto-recommended; override only if needed:
# trainer.hyperparameters.learning_rate = 0.0002
# trainer.hyperparameters.global_batch_size = 16
# trainer.hyperparameters.max_epochs = 5        # (not used by Nova models)

# 3. Train (serverless — the service provisions compute)
training_job = trainer.train(wait=True)
print(training_job.training_job_name, training_job.training_job_status)
```

DPO/RLVR/RLAIF follow the same shape with their own trainer
(`DPOTrainer`, `RLVRTrainer`, `RLAIFTrainer`) and dataset format. RLVR also needs
a reward function registered as a SageMaker Hub **Evaluator ARN**
(`CUSTOM_REWARD_FUNCTION`).

## Key differences from the self-managed training-job path

- **No `Compute(instance_type=...)`** and no `training_image` — that's the whole
  point. Don't add them; the serverless trainer manages compute.
- Inputs are a **registered `DataSet` ARN** and a **`ModelPackageGroup`**, not raw
  S3 channels passed to `.train(input_data_config=[...])`.
- The result is registered as a **model package** in the group, ready to deploy
  (see `llm-inference.md`).

## EULA (gated models)

For Meta/Llama base models you must accept the license: show the user the license
link, get explicit confirmation, then set `ACCEPT_EULA = True` and uncomment the
`accept_eula=ACCEPT_EULA` argument. Non-Meta models: inform the user of the
license but omit the `accept_eula` argument entirely.

## Watch, verify, deploy

- `trainer.train(wait=True)` blocks and reports final status; use `wait=False` to
  run detached, then check with `describe-training-job --training-job-name NAME`.
- Metrics are tracked in MLflow (`training_job.mlflow_details.mlflow_run_id`).
- The customized model lands as a model package in your group — deploy it via
  `llm-inference.md`.

## Cost & cleanup

Serverless training bills only for the run (no idle cluster). Artifacts and the
registered model package sit in S3 / the registry (cheap). Nothing keeps running
afterward — unlike a deployed endpoint.

> Verify the exact trainer arguments and supported base models against current
> AWS documentation and your installed `sagemaker` version — the serverless
> customization API and model catalog evolve.
