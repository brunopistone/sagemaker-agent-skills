#!/usr/bin/env python3
"""
Deploy a trained classic ML model to a SageMaker AI endpoint (SDK V3, ModelBuilder).

Prerequisites:
  pip install sagemaker-serve
  - An execution role; endpoint-usage quota (CPU instances usually already allowed)
  - A trained model: an S3 artifact (model.tar.gz) or a ModelTrainer/TrainingJob

WARNING: a real-time endpoint bills until deleted. This script deletes it at the
end unless KEEP_ENDPOINT = True. For intermittent use, prefer batch transform or
serverless (see classic-ml-inference.md).

Edit CONFIG, then: python deploy_classic_ml_endpoint.py
"""

import numpy as np
from sagemaker.serve import ModelBuilder
from sagemaker.serve.builder.schema_builder import SchemaBuilder

# ----------------------- CONFIG (edit me) -----------------------
MODEL_PATH = "s3://my-bucket/output/model.tar.gz"   # or pass a ModelTrainer/TrainingJob to MODEL
ENDPOINT_NAME = "my-ml-endpoint"
INSTANCE_TYPE = "ml.m5.large"                        # CPU is plenty for classic ML
INSTANCE_COUNT = 1
SAMPLE_INPUT = np.array([[5.1, 3.5, 1.4, 0.2]])
SAMPLE_OUTPUT = np.array([0])
KEEP_ENDPOINT = False
# ----------------------------------------------------------------


def main():
    builder = ModelBuilder(
        model_path=MODEL_PATH,
        schema_builder=SchemaBuilder(sample_input=SAMPLE_INPUT, sample_output=SAMPLE_OUTPUT),
    )

    builder.build()
    endpoint = builder.deploy(
        endpoint_name=ENDPOINT_NAME,
        instance_type=INSTANCE_TYPE,
        initial_instance_count=INSTANCE_COUNT,
    )
    print(f"Endpoint '{ENDPOINT_NAME}' is live.")

    prediction = endpoint.invoke(
        body=b"[[5.1, 3.5, 1.4, 0.2]]",
        content_type="application/json",
        accept="application/json",
    )
    print("Prediction:", prediction)

    if not KEEP_ENDPOINT:
        print("Cleaning up endpoint to stop billing...")
        endpoint.delete()
        endpoint.wait_for_delete()
        print("Deleted.")
    else:
        print("KEEP_ENDPOINT=True — remember to delete it later to stop billing.")


if __name__ == "__main__":
    main()
