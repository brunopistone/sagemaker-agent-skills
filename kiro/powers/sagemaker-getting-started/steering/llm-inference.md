# Deploying & invoking an LLM (SageMaker Python SDK V3)

Goal: get a model behind a callable endpoint. Code uses SDK V3
(`sagemaker-serve` / `sagemaker-core`). Full runnable template:
`templates/deploy_llm_endpoint.py`.

## Questions to ask

1. **Which model?** Something they just fine-tuned (S3 artifact / `ModelTrainer`),
   a HuggingFace ID, or a JumpStart model?
2. **Traffic pattern?** Translate intent:
   - "call it live, low latency" → **real-time endpoint**
   - "batch of inputs, latency doesn't matter" → **async** / batch transform
   - "spiky / rare traffic, minimize idle cost" → **serverless** (small models)
3. **How big is the model?** Use `sizing.md` (inference ≈ 2×params(B) GB fp16 +
   KV-cache headroom) to pick the instance.

## Install

```bash
pip install sagemaker-serve   # pulls sagemaker-core (and sagemaker-train)
```

## Easiest path — `ModelBuilder` (auto-selects container & server)

```python
from sagemaker.serve import ModelBuilder
from sagemaker.serve.builder.schema_builder import SchemaBuilder

builder = ModelBuilder(
    model="meta-llama/Llama-3.1-8B-Instruct",   # HF ID, JumpStart ID, ModelTrainer,
                                                 # TrainingJob, ModelPackage, or a model object
    schema_builder=SchemaBuilder(
        sample_input={"inputs": "Hello, who are you?"},
        sample_output={"generated_text": "I am an assistant."},
    ),
)

model = builder.build()
endpoint = builder.deploy(
    endpoint_name="my-llm-endpoint",
    instance_type="ml.g5.2xlarge",
    initial_instance_count=1,
)

# Invoke
resp = endpoint.invoke(
    body=b'{"inputs": "Write a haiku about the sea."}',
    content_type="application/json",
    accept="application/json",
)
print(resp)

# Streaming / async variants:
# endpoint.invoke_with_response_stream(body=...)
# endpoint.invoke_async(input_location="s3://my-bucket/inputs/req.json")
```

`ModelBuilder` detects the framework/model and picks an appropriate container and
model server (e.g. vLLM/TGI for LLMs). For gated models, provide `HF_TOKEN` via
the model's environment.

## Lower-level path (full control over container/env)

When you need a specific container or tuned server flags, create the resources
directly with `sagemaker-core`:

```python
from sagemaker.core.resources import Model, EndpointConfig, Endpoint
from sagemaker.core.shapes import ContainerDefinition, ProductionVariant

model = Model.create(
    model_name="my-llm",
    primary_container=ContainerDefinition(
        image="<account>.dkr.ecr.<region>.amazonaws.com/<vllm-or-tgi-image>",
        environment={"HF_MODEL_ID": "meta-llama/Llama-3.1-8B-Instruct", "HF_TOKEN": "..."},
    ),
    execution_role_arn=role_arn,
)
endpoint_config = EndpointConfig.create(
    endpoint_config_name="my-llm-config",
    production_variants=[ProductionVariant(
        variant_name="primary", model_name="my-llm",
        instance_type="ml.g5.2xlarge", initial_instance_count=1)],
)
endpoint = Endpoint.create(endpoint_name="my-llm-endpoint", endpoint_config_name="my-llm-config")
endpoint.wait_for_status("InService")
endpoint.invoke(body=b'{"inputs": "hi"}', content_type="application/json")
```

For very large models on GPUs you may attach an **InferenceComponent** to bind the
model with compute requirements — only reach for it when a single variant won't do.

## Prerequisites

Execution role, region, and — for gated models — `HF_TOKEN`/EULA. Inference
instances need their own **quota** (e.g. _"ml.g5.2xlarge for endpoint usage"_).

## Verify & (critically) clean up

- Test with a sample payload right after deploy; confirm a sensible response.
- **An endpoint bills continuously until deleted.** Always give the cleanup:

```python
endpoint.delete()
endpoint.wait_for_delete()
endpoint_config.delete()
model.delete()
```

This is the #1 surprise-bill source for newcomers — state it plainly.
