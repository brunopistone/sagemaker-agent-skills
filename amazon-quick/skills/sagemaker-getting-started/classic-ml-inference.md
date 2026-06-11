# Deploying a classic ML model (SDK V3)

Goal: serve a trained non-LLM model (sklearn/XGBoost/PyTorch) behind an endpoint.
Code uses SDK V3 (`sagemaker-serve` / `sagemaker-core`). Full template:
`templates/deploy_classic_ml_endpoint.py`.

## Questions to ask

1. **Where is the trained model?** An S3 artifact from a training job, a
   `ModelTrainer`/`TrainingJob` object, or a local model file to upload.
2. **Traffic pattern?** Real-time (default), serverless (spiky/cheap), or batch
   transform (offline scoring of a large file).
3. **Custom inference logic?** Does it need pre/post-processing, or is raw
   predict enough?

## Install

```bash
pip install sagemaker-serve
```

## Easiest path — `ModelBuilder` from a training artifact

```python
from sagemaker.serve import ModelBuilder
from sagemaker.serve.builder.schema_builder import SchemaBuilder
import numpy as np

builder = ModelBuilder(
    model=training_job,                      # ModelTrainer/TrainingJob, or model_path="s3://.../model.tar.gz"
    schema_builder=SchemaBuilder(
        sample_input=np.array([[5.1, 3.5, 1.4, 0.2]]),
        sample_output=np.array([0]),
    ),
)

model = builder.build()
endpoint = builder.deploy(
    endpoint_name="my-ml-endpoint",
    instance_type="ml.m5.large",             # CPU is plenty for classic ML
    initial_instance_count=1,
)

prediction = endpoint.invoke(
    body=b"[[5.1, 3.5, 1.4, 0.2]]",
    content_type="application/json",
    accept="application/json",
)
print(prediction)
```

`SchemaBuilder` infers serialization from the sample input/output, so callers can
send plain JSON. For custom pre/post-processing, provide an `InferenceSpec`
implementation to `ModelBuilder(inference_spec=...)`.

## Serverless / batch variants

- **Serverless** (scale-to-zero, pay-per-request, small models): configure a
  serverless inference config on deploy instead of an instance type.
- **Batch transform** (score a big S3 file offline, no always-on endpoint): build
  the model, then run a transform job over an S3 input prefix. Cheapest for
  one-shot bulk scoring — nothing stays running.

## Prerequisites

Execution role, region, and **endpoint quota** for the instance (CPU instances
are usually already available). No GPU needed for typical classic ML.

## Verify & clean up

- Send a sample payload; confirm a sensible prediction.
- **A real-time endpoint bills until deleted:**

```python
endpoint.delete()
endpoint.wait_for_delete()
```

Also delete the endpoint config and model if you created them explicitly. Batch
transform and serverless avoid idle billing — prefer them for intermittent use.
