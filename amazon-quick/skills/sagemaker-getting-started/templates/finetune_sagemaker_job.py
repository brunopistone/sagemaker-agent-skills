#!/usr/bin/env python3
"""
Fine-tune an LLM as a SageMaker AI managed training job (SDK V3).

Prerequisites:
  pip install sagemaker-train
  - An execution role (in Studio: get_execution_role(); locally: pass a role ARN)
  - Training data in S3 (e.g. JSONL of prompt/response)
  - Service quota for the chosen GPU instance
  - For gated models: accept the HF license and set HF_TOKEN

Edit the CONFIG block, then: python finetune_sagemaker_job.py
"""

from sagemaker.train import ModelTrainer
from sagemaker.train.configs import SourceCode, Compute, InputData, StoppingCondition
from sagemaker.core.helper.session_helper import Session, get_execution_role
from sagemaker.core import image_uris

# ----------------------- CONFIG (edit me) -----------------------
INSTANCE_TYPE = "ml.g5.2xlarge"     # see sizing.md; one A10G 24GB fits 8B QLoRA
INSTANCE_COUNT = 1
TRAIN_DATA_S3 = "s3://my-bucket/data/train/"
SOURCE_DIR = "src"                  # local dir containing train.py + requirements.txt
ENTRY_SCRIPT = "train.py"
MAX_RUNTIME_HOURS = 24
ROLE_ARN = None                     # None -> use get_execution_role() (works in Studio)
HF_TOKEN = None                     # set for gated models (Llama, etc.)
# ----------------------------------------------------------------


def main():
    session = Session()
    region = session.boto_region_name
    role = ROLE_ARN or get_execution_role()

    training_image = image_uris.retrieve(
        framework="pytorch", region=region, version="2.3",
        instance_type=INSTANCE_TYPE, image_scope="training",
    )

    env = {}
    if HF_TOKEN:
        env["HF_TOKEN"] = HF_TOKEN

    trainer = ModelTrainer(
        training_image=training_image,
        source_code=SourceCode(source_dir=SOURCE_DIR, entry_script=ENTRY_SCRIPT),
        compute=Compute(instance_type=INSTANCE_TYPE, instance_count=INSTANCE_COUNT),
        stopping_condition=StoppingCondition(max_runtime_in_seconds=MAX_RUNTIME_HOURS * 3600),
        environment=env or None,
        role=role,
    )

    trainer.train(
        input_data_config=[InputData(channel_name="train", data_source=TRAIN_DATA_S3)],
        wait=True,
    )

    job = trainer._latest_training_job
    print("Training job complete.")
    print("Model artifact:", getattr(job, "model_artifacts", "see S3 output path"))


if __name__ == "__main__":
    main()
