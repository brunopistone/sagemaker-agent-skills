# Package 3: sagemaker-serve

**Namespace:** `sagemaker.serve`
**Role:** Model deployment, inference, model servers
**PyPI:** `sagemaker-serve` (depends on sagemaker-core + sagemaker-train)

## Key Classes

| Class                     | File                                       | Purpose                                                  |
| ------------------------- | ------------------------------------------ | -------------------------------------------------------- |
| **`ModelBuilder`**        | `model_builder.py` (~48K lines)            | Primary deployment interface (replaces V2 Model classes) |
| `InferenceSpec`           | `spec/inference_spec.py`                   | Abstract base for custom inference logic                 |
| `SchemaBuilder`           | `builder/schema_builder.py`                | Auto-detect serialization schemas                        |
| `CustomPayloadTranslator` | `marshalling/custom_payload_translator.py` | Custom serialization                                     |
| `BedrockModelBuilder`     | `bedrock_model_builder.py`                 | Deploy to Amazon Bedrock                                 |
| `LocalEndpoint`           | `local_resources.py`                       | Local endpoint abstraction                               |

## Model Servers (8 supported)

| Server          | Namespace                               | Use Case                                    |
| --------------- | --------------------------------------- | ------------------------------------------- |
| **TorchServe**  | `model_server/torchserve/`              | PyTorch models (.mar archives)              |
| **Triton**      | `model_server/triton/`                  | Multi-framework, high-performance           |
| **TGI**         | `model_server/tgi/`                     | Large Language Models (continuous batching) |
| **TEI**         | `model_server/tei/`                     | Embedding models                            |
| **DJL Serving** | `model_server/djl_serving/`             | Universal multi-framework                   |
| **TF Serving**  | `model_server/tensorflow_serving/`      | TensorFlow SavedModel                       |
| **MMS**         | `model_server/multi_model_server/`      | Multi-model endpoints                       |
| **SMD**         | `model_server/smd/`                     | Fully custom inference                      |
| **In-Process**  | `model_server/in_process_model_server/` | FastAPI in current process                  |

## Deployment Modes

| Mode                 | Enum      | Description                                     |
| -------------------- | --------- | ----------------------------------------------- |
| `IN_PROCESS`         | `Mode(1)` | Run in current Python process (fastest for dev) |
| `LOCAL_CONTAINER`    | `Mode(2)` | Run in local Docker container                   |
| `SAGEMAKER_ENDPOINT` | `Mode(3)` | Deploy to SageMaker cloud endpoint              |

## Inference Types

- **Real-time**: Standard endpoints via `deploy()`
- **Async**: `AsyncInferenceConfig` with S3 output polling
- **Batch**: `BatchTransformInferenceConfig` via `transformer()`
- **Serverless**: `ServerlessInferenceConfig`
- **Multi-model**: `ModelBuilder(modelbuilder_list=[mb1, mb2])` with InferenceComponents

## ModelBuilder.build() + deploy() Flow

1. Detect framework/model type (PyTorch, TF, HuggingFace, XGBoost, etc.)
2. Auto-select container image and model server
3. Prepare model artifacts (pickle, .mar, etc.)
4. Upload to S3
5. Create `sagemaker.core.resources.Model`
6. Create `EndpointConfig` and `Endpoint`
7. Return `sagemaker.core.resources.Endpoint`

## Input Sources for `model` Parameter

- Python model object (PyTorch, TF, sklearn, XGBoost)
- `ModelTrainer` instance (chain from training)
- `TrainingJob` instance
- `ModelPackage` instance
- HuggingFace model ID string
- JumpStart model ID string
- List of models (multi-model)
