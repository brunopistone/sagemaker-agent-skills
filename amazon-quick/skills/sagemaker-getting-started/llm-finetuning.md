# Fine-tuning an LLM (SageMaker Python SDK V3)

Goal: take an open model (Llama, Mistral, Qwen, Nova, ...) and adapt it to the
user's data. Code uses SDK V3 (`sagemaker-train`). Full runnable template:
`templates/finetune_sagemaker_job.py`.

> **Easiest path first:** if the base model + technique are supported, prefer
> **serverless model customization** (`serverless-customization.md`) — no
> instance to size, no script to write, no quota to request. This file covers the
> self-managed training-job path; reach for it when you need custom training
> logic, an unsupported model, or full control over the compute.

## Questions to ask (plain language)

1. **Which model?** If unsure, suggest a small open one (e.g. Llama 3 8B) —
   cheaper, faster, easier to fit.
2. **What technique?** Translate intent → technique:
   - "teach it my examples / instructions" → **SFT** (supervised fine-tuning)
   - "make it prefer good answers over bad" → **DPO**
   - "limited GPU / cheap" → **LoRA / QLoRA** (parameter-efficient)
   - "full quality, big GPUs available" → full fine-tuning
3. **Data?** Where is it, what format (commonly JSONL of prompt/response)? If they
   have none, offer a tiny public example dataset to prove the pipeline first.
4. **Scale/urgency?** Feeds the sizing step.

## Size first

Use `sizing.md` to pick an instance from the model size + technique, e.g.
"Llama 3 8B + QLoRA → ~4 GB → `ml.g5.2xlarge`". State instance type and rough time.

## Install

```bash
pip install sagemaker-train   # pulls sagemaker-core; add sagemaker-serve to deploy
```

## Pattern A — `ModelTrainer` with your own training script (most flexible)

```python
from sagemaker.train import ModelTrainer, Mode
from sagemaker.train.configs import SourceCode, Compute, InputData, StoppingCondition
from sagemaker.core.helper.session_helper import Session, get_execution_role
from sagemaker.core import image_uris

role = get_execution_role()            # in Studio; locally pass a role ARN string
region = Session().boto_region_name

# A framework training container (or your own ECR image / a DLC URI)
training_image = image_uris.retrieve(
    framework="pytorch", region=region, version="2.3",
    instance_type="ml.g5.2xlarge", image_scope="training",
)

trainer = ModelTrainer(
    training_image=training_image,
    source_code=SourceCode(source_dir="src", entry_script="train.py"),
    compute=Compute(instance_type="ml.g5.2xlarge", instance_count=1),
    stopping_condition=StoppingCondition(max_runtime_in_seconds=24 * 3600),
    role=role,
)

trainer.train(
    input_data_config=[InputData(channel_name="train", data_source="s3://my-bucket/data/train/")],
    wait=True,   # streams logs; set False to run detached
)
# Result: a TrainingJob; artifact lands in the S3 output path.
training_job = trainer._latest_training_job
```

Your `train.py` runs inside the container. Conventions to explain:

- input data is at `/opt/ml/input/data/<channel>/`,
- save the final model to `/opt/ml/model/` (SageMaker tars it to S3 automatically),
- hyperparameters arrive as CLI args / env vars.
  Use any library inside (e.g. `transformers` + `peft` for LoRA/QLoRA).

## Pattern B — built-in fine-tuning trainers (serverless, least code)

`sagemaker-train` ships higher-level trainers (`SFTTrainer`, `DPOTrainer`,
`RLVRTrainer`, `RLAIFTrainer`) that run **serverless** — you pass a base model, a
registered dataset, and a technique, and the service manages the compute (no
`Compute(instance_type=...)`, no container). This is the recommended easy path.

Because the API differs meaningfully from Pattern A (it uses a registered
`DataSet` ARN and a `ModelPackageGroup`, not raw S3 channels), it has its own
file: see **`serverless-customization.md`** for the full SFT/DPO/RLVR/RLAIF flow
and a runnable example.

## Pattern C — launch a curated recipe as a managed job

```python
trainer = ModelTrainer.from_recipe(
    recipe="fine-tuning/llama/hf_llama3_8b_seq8k_gpu_fine_tuning",
    compute=Compute(instance_type="ml.g5.12xlarge", instance_count=1),
    role=role,
)
trainer.train(input_data_config=[...], wait=True)
```

The same recipe families also run on **HyperPod** for big/long jobs — see
`hyperpod.md`.

## Prerequisites specific to fine-tuning

- **Gated model access**: accept the HuggingFace license + provide `HF_TOKEN` to
  the job (env var). JumpStart models may need EULA acceptance.
- Data in **S3** (the job reads from the channel).
- Correct **quota** for the GPU instance (see `prerequisites.md`).

## Run, watch, verify, clean up

- `wait=True` streams logs; otherwise watch in the SageMaker console / CloudWatch.
- Success = job `Completed`, model artifact in the S3 output path.
- Nothing keeps billing after a managed job finishes (artifacts in S3 are cheap).
- Next step is usually deployment → `llm-inference.md`.
