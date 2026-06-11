#!/usr/bin/env python3
"""
Train a classic ML model (sklearn example) as a SageMaker AI job (SDK V3).

Prerequisites:
  pip install sagemaker-train
  - An execution role; training data in S3
  - CPU instances (ml.m5/ml.c5) are usually already in quota

Layout:
  this_script.py
  src/
    train.py            # the example below
    requirements.txt    # optional extra deps

Edit CONFIG, then: python train_classic_ml_job.py

----------------------------------------------------------------------
Example src/train.py:

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
----------------------------------------------------------------------
"""

from sagemaker.train import ModelTrainer
from sagemaker.train.configs import SourceCode, Compute, InputData
from sagemaker.core.helper.session_helper import Session, get_execution_role
from sagemaker.core import image_uris

# ----------------------- CONFIG (edit me) -----------------------
INSTANCE_TYPE = "ml.m5.xlarge"      # CPU is fine for most classic ML
INSTANCE_COUNT = 1
TRAIN_DATA_S3 = "s3://my-bucket/data/train/"
SOURCE_DIR = "src"
ENTRY_SCRIPT = "train.py"
SKLEARN_VERSION = "1.2-1"
ROLE_ARN = None                     # None -> get_execution_role()
# ----------------------------------------------------------------


def main():
    session = Session()
    region = session.boto_region_name
    role = ROLE_ARN or get_execution_role()

    training_image = image_uris.retrieve(
        framework="sklearn", region=region, version=SKLEARN_VERSION,
        instance_type=INSTANCE_TYPE, image_scope="training",
    )

    trainer = ModelTrainer(
        training_image=training_image,
        source_code=SourceCode(source_dir=SOURCE_DIR, entry_script=ENTRY_SCRIPT),
        compute=Compute(instance_type=INSTANCE_TYPE, instance_count=INSTANCE_COUNT),
        role=role,
    )
    trainer.train(
        input_data_config=[InputData(channel_name="train", data_source=TRAIN_DATA_S3)],
        wait=True,
    )
    print("Training complete. Model artifact written to the S3 output path.")


if __name__ == "__main__":
    main()
