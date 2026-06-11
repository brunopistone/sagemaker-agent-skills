# Training a classic ML model (SDK V3)

Goal: train a non-LLM model (tabular, classic CV/NLP) on SageMaker. Usually CPU
or a single small GPU — much cheaper and simpler than LLM work. Code uses SDK V3
(`sagemaker-train`). Full template: `templates/train_classic_ml_job.py`.

## Questions to ask

1. **Framework?** sklearn, XGBoost, PyTorch, TensorFlow, or custom.
2. **Data?** Location (S3 / local to upload) and format (CSV, parquet, images).
3. **Existing training script?** If yes, we wrap it; if not, we scaffold one.

## Install

```bash
pip install sagemaker-train
```

## Pattern — `ModelTrainer` with your own script

```python
from sagemaker.train import ModelTrainer
from sagemaker.train.configs import SourceCode, Compute, InputData
from sagemaker.core.helper.session_helper import Session, get_execution_role
from sagemaker.core import image_uris

role = get_execution_role()
region = Session().boto_region_name

# Pick a framework container; CPU instance is fine for most classic ML
training_image = image_uris.retrieve(
    framework="sklearn", region=region, version="1.2-1",
    instance_type="ml.m5.xlarge", image_scope="training",
)

trainer = ModelTrainer(
    training_image=training_image,
    source_code=SourceCode(source_dir="src", entry_script="train.py"),
    compute=Compute(instance_type="ml.m5.xlarge", instance_count=1),
    role=role,
)
trainer.train(
    input_data_config=[InputData(channel_name="train", data_source="s3://my-bucket/data/train/")],
    wait=True,
)
```

## The training-script contract (explain this to newcomers)

SageMaker runs `train.py` inside the container with conventions:

- input data mounted at `/opt/ml/input/data/<channel>/`,
- hyperparameters arrive as CLI args / env vars,
- **save the model to `/opt/ml/model/`** — SageMaker tars that dir into the S3
  artifact automatically.

Minimal `src/train.py`:

```python
import argparse, os, joblib, pandas as pd
from sklearn.ensemble import RandomForestClassifier

p = argparse.ArgumentParser()
p.add_argument("--n-estimators", type=int, default=100)
args = p.parse_args()

data_dir = os.environ.get("SM_CHANNEL_TRAIN", "/opt/ml/input/data/train")
df = pd.read_csv(os.path.join(data_dir, "train.csv"))
X, y = df.drop(columns=["target"]), df["target"]

model = RandomForestClassifier(n_estimators=args.n_estimators).fit(X, y)

model_dir = os.environ.get("SM_MODEL_DIR", "/opt/ml/model")
joblib.dump(model, os.path.join(model_dir, "model.joblib"))
```

Getting these paths right avoids the usual "it ran but produced no model" confusion.

## Hardware sizing

Classic ML rarely needs a GPU. Default to CPU (`ml.m5`/`ml.c5`); move to a GPU
(`ml.g5`) only if the framework + data justify it. Bigger data → bigger instance
or distributed, not automatically a GPU. CPU quotas are usually already available.

## Verify & cleanup

Job `Completed` + model artifact in the S3 output path. Managed jobs stop billing
on completion. Next step is usually `classic-ml-inference.md`.
