# Fine-tuning an LLM (SageMaker Python SDK V3)

Goal: take an open model (Llama, Mistral, Qwen, Nova, ...) and adapt it to the
user's data. Code uses SDK V3 (`sagemaker-train`). Full runnable template:
`templates/finetune_sagemaker_job.py`.

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
4. **Scale/urgency?** Drives which option below, and (for managed jobs) the sizing step.

## Pick the option (easiest first)

| # | Option | You manage | Use when |
|---|--------|-----------|----------|
| 1 | **Serverless customization** (`serverless-customization.md`) | nothing — base model + dataset + technique | the base model & technique are supported; you want the easiest path |
| 2 | **Managed job, your script** (Option A below) | instance type + a `train.py` | custom training logic or an unsupported model |
| 3 | **Managed job from a recipe** (Option B below) | instance type | a curated recipe fits your model/technique |
| 4 | **HyperPod recipe job** (`hyperpod.md`) | a persistent cluster | big/long runs; same recipe, on a resilient cluster |
| 5 | **HyperPod custom PyTorch job** (Option C below) | cluster + your container/script | custom code at scale on a resilient cluster |

Options 1–3 are **managed (no cluster)**; 4–5 run on a **HyperPod cluster** you
provision and keep running. Default to **#1 serverless** for newcomers; move down
the list only when you need more control or scale.

## Size first (managed jobs only)

For Options A/B (and HyperPod), use `sizing.md` to pick an instance from the model
size + technique, e.g. "Llama 3 8B + QLoRA → ~4 GB → `ml.g5.2xlarge`". State
instance type and rough time. (Serverless customization skips this — the service
picks the compute.)

## Install

```bash
pip install sagemaker-train   # pulls sagemaker-core; add sagemaker-serve to deploy
```

## Option A — managed job, `ModelTrainer` with your own training script

Most flexible managed path: you bring a `train.py` and pick the instance.

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

## Option B — managed job from a curated recipe

```python
trainer = ModelTrainer.from_recipe(
    recipe="fine-tuning/llama/hf_llama3_8b_seq8k_gpu_fine_tuning",
    compute=Compute(instance_type="ml.g5.12xlarge", instance_count=1),
    role=role,
)
trainer.train(input_data_config=[...], wait=True)
```

The same recipe families also run on **HyperPod** (Option below / `hyperpod.md`).

## Option C — fine-tune on a HyperPod cluster

For big/long/failure-prone runs on a **persistent, resilient cluster** (you must
already have a HyperPod cluster — see `hyperpod.md` for when/how). Two ways:

- **Recipe job** — `hyp create hyp-recipe-job ...`: the same curated recipes as
  Option B, driven on the cluster.
- **Custom PyTorch job** — `hyp create hyp-pytorch-job ...` (SDK:
  `HyperPodPytorchJob`): bring your own PyTorch training code/container, the
  HyperPod analogue of Option A. Supports multi-node, GPU/Neuron/EFA, and
  auto-resume on node failure.

Full commands and SDK usage are in **`hyperpod-cli-reference.md`**. Pick HyperPod
only when a managed job (Options 1–3) isn't enough — it's a cluster you own and
pay for while it runs.

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
