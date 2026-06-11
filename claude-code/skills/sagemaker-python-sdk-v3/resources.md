# Core Resource Usage

Two levels of API:

- **High-level API**: `ModelTrainer`, `Processor`, `ModelBuilder` — handles packaging, defaults, and orchestration
- **Low-level API**: Resource classes in `sagemaker.core.resources` — thin wrappers around SageMaker API calls

All resource classes follow a consistent pattern: `create()`, `get()`, `get_all()`, `delete()`, plus resource-specific methods like `wait()`, `stop()`, `update()`, `invoke()`.

## TrainingJob

```python
# HIGH-LEVEL (recommended): via ModelTrainer
from sagemaker.train import ModelTrainer
from sagemaker.core.helper.session_helper import Session, get_execution_role

trainer = ModelTrainer(
    training_image="763104351884.dkr.ecr.us-west-2.amazonaws.com/pytorch-training:2.0-gpu-py310",
    source_code=SourceCode(source_dir="src", entry_script="train.py"),
    compute=Compute(instance_type="ml.g5.xlarge", instance_count=1),
    role=get_execution_role(),
)
trainer.train(input_data_config=[InputData(channel_name="train", data_source="s3://bucket/data")], wait=True)
training_job = trainer._latest_training_job  # returns TrainingJob resource

# LOW-LEVEL: via TrainingJob.create() directly
from sagemaker.core.resources import TrainingJob

job = TrainingJob.create(
    training_job_name="my-job",
    role_arn="arn:aws:iam::...",
    algorithm_specification=AlgorithmSpecification(training_image="...", training_input_mode="File"),
    resource_config=ResourceConfig(instance_type="ml.m5.large", instance_count=1, volume_size_in_gb=30),
    output_data_config=OutputDataConfig(s3_output_path="s3://bucket/output"),
    input_data_config=[Channel(channel_name="train", data_source=DataSource(...))],
    stopping_condition=StoppingCondition(max_runtime_in_seconds=3600),
)
job.wait(logs=True)          # Poll until complete, stream CloudWatch logs
job.stop()                   # Stop early
job = TrainingJob.get("my-job")  # Retrieve existing job
```

## ProcessingJob

```python
# HIGH-LEVEL (recommended): via Processor / ScriptProcessor
from sagemaker.core import Processor, ScriptProcessor
from sagemaker.core.processing import ProcessingInput, ProcessingOutput

processor = ScriptProcessor(
    role="arn:aws:iam::...",
    image_uri="763104351884.dkr.ecr.us-west-2.amazonaws.com/sklearn-processing:1.0",
    command=["python3"],
    instance_count=1,
    instance_type="ml.m5.xlarge",
)
processor.run(
    inputs=[ProcessingInput(source="s3://bucket/input", destination="/opt/ml/processing/input")],
    outputs=[ProcessingOutput(source="/opt/ml/processing/output", destination="s3://bucket/output")],
    code="scripts/preprocess.py",
    wait=True,
)

# LOW-LEVEL: via ProcessingJob.create()
from sagemaker.core.resources import ProcessingJob

job = ProcessingJob.create(
    processing_job_name="my-processing-job",
    role_arn="arn:aws:iam::...",
    processing_resources=ProcessingResources(cluster_config=ProcessingClusterConfig(
        instance_count=1, instance_type="ml.m5.xlarge", volume_size_in_gb=30)),
    app_specification=AppSpecification(image_uri="...", container_entrypoint=["python3", "/opt/ml/code/process.py"]),
)
job.wait()
job.stop()
```

## Model, EndpointConfig, Endpoint

```python
# HIGH-LEVEL (recommended): via ModelBuilder
from sagemaker.serve import ModelBuilder

builder = ModelBuilder(
    model="my-model-id",            # HuggingFace ID, JumpStart ID, ModelTrainer, or Python model object
    schema_builder=SchemaBuilder(sample_input=..., sample_output=...),
)
model = builder.build()             # Creates sagemaker.core.resources.Model
endpoint = builder.deploy(          # Creates EndpointConfig + Endpoint, returns Endpoint resource
    endpoint_name="my-endpoint",
    instance_type="ml.g5.xlarge",
    initial_instance_count=1,
)

# Invoke the endpoint
response = endpoint.invoke(body=payload, content_type="application/json", accept="application/json")
response = endpoint.invoke_async(input_location="s3://bucket/input.json")
response = endpoint.invoke_with_response_stream(body=payload)

# LOW-LEVEL: direct resource creation
from sagemaker.core.resources import Model, EndpointConfig, Endpoint
from sagemaker.core.shapes import ContainerDefinition, ProductionVariant

model = Model.create(
    model_name="my-model",
    primary_container=ContainerDefinition(image="...", model_data_url="s3://bucket/model.tar.gz"),
    execution_role_arn="arn:aws:iam::...",
)

endpoint_config = EndpointConfig.create(
    endpoint_config_name="my-config",
    production_variants=[ProductionVariant(
        variant_name="primary",
        model_name="my-model",
        instance_type="ml.g5.xlarge",
        initial_instance_count=1,
    )],
)

endpoint = Endpoint.create(endpoint_name="my-endpoint", endpoint_config_name="my-config")
endpoint.wait_for_status("InService")   # Poll until ready
endpoint.invoke(body=b'{"input": "hello"}', content_type="application/json")

# Cleanup
endpoint.delete()
endpoint.wait_for_delete()
endpoint_config.delete()
model.delete()
```

## InferenceComponent

```python
from sagemaker.core.resources import InferenceComponent
from sagemaker.core.shapes import InferenceComponentSpecification, InferenceComponentRuntimeConfig

# Create (attaches to an existing endpoint)
ic = InferenceComponent.create(
    inference_component_name="my-component",
    endpoint_name="my-endpoint",          # or an Endpoint object
    variant_name="primary",
    specification=InferenceComponentSpecification(
        model_name="my-model",
        compute_resource_requirements=InferenceComponentComputeResourceRequirements(
            number_of_cpu_cores_required=2,
            min_memory_required_in_mb=4096,
        ),
    ),
    runtime_config=InferenceComponentRuntimeConfig(copy_count=1),
)
ic.wait_for_status("InService")

# Invoke via the parent endpoint (specify inference_component_name)
endpoint.invoke(body=payload, inference_component_name="my-component")

# Update and lifecycle
ic.update(runtime_config=InferenceComponentRuntimeConfig(copy_count=2))
ic.wait_for_status("InService")
ic.delete()
ic.wait_for_delete()
```

## Full LLM Deployment with Core SDK (vLLM + Inference Components)

End-to-end example deploying a HuggingFace model on GPU with the Core SDK directly:

```python
from sagemaker.core.helper.session_helper import Session, get_execution_role
from sagemaker.core.resources import EndpointConfig, Endpoint, Model, InferenceComponent
from sagemaker.core.shapes import (
    ProductionVariant, ContainerDefinition, ModelDataSource, S3ModelDataSource,
    InferenceComponentSpecification, InferenceComponentComputeResourceRequirements,
    InferenceComponentRuntimeConfig,
)

sess = Session()
role = get_execution_role()
region = sess.boto_region_name

# 1. Create EndpointConfig (GPU instance, no model yet — model comes via InferenceComponent)
endpoint_config = EndpointConfig.create(
    endpoint_config_name="my-llm-config",
    execution_role_arn=role,
    production_variants=[
        ProductionVariant(
            variant_name="AllTraffic",
            instance_type="ml.g5.12xlarge",
            initial_instance_count=1,
            model_data_download_timeout_in_seconds=700,
            inference_ami_version="al2-ami-sagemaker-inference-gpu-3-1",
            routing_config={"routing_strategy": "LEAST_OUTSTANDING_REQUESTS"},
        )
    ],
)

# 2. Create Endpoint
endpoint = Endpoint.create(endpoint_name="my-llm-endpoint", endpoint_config_name="my-llm-config")
endpoint.wait_for_status("InService")

# 3. Create Model with vLLM container and environment config
image_uri = f"763104351884.dkr.ecr.{region}.amazonaws.com/vllm:0.21.0-gpu-py312-cu130-ubuntu22.04-sagemaker"

model = Model.create(
    model_name="my-llm-model",
    primary_container=ContainerDefinition(
        image=image_uri,
        model_data_source=ModelDataSource(
            s3_data_source=S3ModelDataSource(
                s3_uri="s3://bucket/model-artifacts/",  # Optional: S3 prefix with config files
                s3_data_type="S3Prefix",
                compression_type="None",
            )
        ),
        environment={
            "SM_VLLM_MODEL": "Qwen/Qwen3.5-4B",      # HuggingFace model ID
            "HF_TOKEN": "...",                          # For gated models
            "SM_VLLM_DTYPE": "bfloat16",
            "SM_VLLM_GPU_MEMORY_UTILIZATION": "0.9",
            "SM_VLLM_MAX_MODEL_LEN": "131072",
            "SM_VLLM_TENSOR_PARALLEL_SIZE": "4",
        },
    ),
    execution_role_arn=role,
)

# 4. Create InferenceComponent (binds model to endpoint with resource requirements)
ic = InferenceComponent.create(
    inference_component_name="my-llm-ic",
    endpoint_name="my-llm-endpoint",
    variant_name="AllTraffic",
    specification=InferenceComponentSpecification(
        model_name="my-llm-model",
        compute_resource_requirements=InferenceComponentComputeResourceRequirements(
            min_memory_required_in_mb=10240,
            number_of_accelerator_devices_required=4,
        ),
    ),
    runtime_config=InferenceComponentRuntimeConfig(copy_count=1),
)
ic.wait_for_status("InService")

# 5. Invoke (OpenAI-compatible chat completions via sagemaker-runtime)
import boto3, json
sm_runtime = boto3.client("sagemaker-runtime", region_name=region)

response = sm_runtime.invoke_endpoint_with_response_stream(
    EndpointName="my-llm-endpoint",
    InferenceComponentName="my-llm-ic",
    Body=json.dumps({
        "messages": [{"role": "user", "content": "Hello!"}],
        "max_tokens": 512,
        "stream": True,
    }),
    ContentType="application/json",
)

# 6. Cleanup (order matters: IC → Model → Endpoint → EndpointConfig)
ic.delete()
ic.wait_for_delete()
model.delete()
endpoint.delete()
endpoint.wait_for_delete()
endpoint_config.delete()
```

## Resource Lifecycle Summary

| Operation                       | TrainingJob | ProcessingJob | Model | EndpointConfig | Endpoint | InferenceComponent |
| ------------------------------- | :---------: | :-----------: | :---: | :------------: | :------: | :----------------: |
| `create()`                      |      x      |       x       |   x   |       x        |    x     |         x          |
| `get()`                         |      x      |       x       |   x   |       x        |    x     |         x          |
| `get_all()`                     |      x      |       x       |   x   |       x        |    x     |         x          |
| `update()`                      |      x      |       -       |   -   |       -        |    x     |         x          |
| `delete()`                      |      x      |       x       |   x   |       x        |    x     |         x          |
| `stop()`                        |      x      |       x       |   -   |       -        |    -     |         -          |
| `wait()`                        |      x      |       x       |   -   |       -        |    -     |         -          |
| `wait_for_status()`             |      -      |       -       |   -   |       -        |    x     |         x          |
| `wait_for_delete()`             |      x      |       -       |   -   |       -        |    x     |         x          |
| `invoke()`                      |      -      |       -       |   -   |       -        |    x     |         -          |
| `invoke_async()`                |      -      |       -       |   -   |       -        |    x     |         -          |
| `invoke_with_response_stream()` |      -      |       -       |   -   |       -        |    x     |         -          |
