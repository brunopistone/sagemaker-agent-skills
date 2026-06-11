# Package 1: sagemaker-core

**Namespace:** `sagemaker.core` (+ deprecated `sagemaker.lineage` shim)
**Role:** Foundation primitives, AWS API wrappers, configuration, shared utilities
**PyPI:** `sagemaker-core`

## Key Modules

| Module | Purpose | Key Classes/Functions |
|--------|---------|----------------------|
| `resources.py` | Auto-generated SageMaker resource classes (~1.57MB) | `TrainingJob`, `Model`, `Endpoint`, `EndpointConfig`, `ProcessingJob`, `InferenceComponent`, `ModelPackage`, etc. |
| `processing.py` | High-level processing job API | `Processor`, `ScriptProcessor`, `FrameworkProcessor`, `FeatureStoreOutput` |
| `spark/processing.py` | Spark processing jobs | `PySparkProcessor`, `SparkJarProcessor` |
| `shapes/` | Generated data shapes (Pydantic models) | All SageMaker API shapes |
| `config/` | Intelligent defaults system | `SageMakerConfig`, `load_sagemaker_config()`, `validate_sagemaker_config()` |
| `workflow/` | Pipeline variable primitives | `Parameter`, `ParameterString`, `ExecutionVariables`, `Properties`, `Join`, `JsonGet`, `Condition*` |
| `image_retriever/` + `image_uris.py` | Framework image URI resolution | `retrieve()`, `ImageRetriever`, 50+ JSON config files |
| `jumpstart/` | Pre-trained model discovery | `JumpStartModelsAccessor`, `JumpStartConfig`, model search/filter |
| `remote_function/` | Remote Python execution on SageMaker | `@remote` decorator, `RemoteExecutor`, `CheckpointLocation` |
| `experiments/` | Experiment/trial tracking | `Experiment`, `Run`, `_Trial`, `_TrialComponent` |
| `lineage/` (`sagemaker.lineage` is deprecated shim) | Data lineage tracking | `Action`, `Artifact`, `Association`, `Context`, `LineageQuery` |
| `local/` | Local mode execution | `LocalSession` |
| `helper/session_helper.py` | Session management | `Session`, `get_execution_role()` |
| `s3/` | S3 upload/download utilities | `S3Uploader`, `S3Downloader`, `parse_s3_url()` |
| `apiutils/` | Boto response/request conversion | `ApiObject`, `Record`, case conversion utilities |
| `serializers/`, `deserializers/` | Inference data serialization | `BaseSerializer`, `BaseDeserializer` |
| `telemetry/` | Feature usage tracking + attribution | `_telemetry_emitter` decorator, `Feature` enum, `Attribution`, `set_attribution()` |
| `token_generator/` | SigV4 bearer token generation for SageMaker API auth | `SageMakerTokenGenerator` |
| `partner_app/` | Partner app authentication | `PartnerAppAuthProvider` |
| `modules/train/` | Container driver framework | `container_drivers/` (torchrun, MPI), `sm_recipes/` |
| `mlflow/` | MLflow integration | `forward_sagemaker_metrics` |
| `model_monitor/` | Model monitoring | Quality monitoring configs, alert definitions |
| `model_card/` | Model documentation | Model card management |

## Configuration System
Priority order (highest to lowest):
1. Explicit user parameters
2. SDK config (`SAGEMAKER_ADMIN_CONFIG_OVERRIDE` / `SAGEMAKER_USER_CONFIG_OVERRIDE`)
3. Hard-coded defaults

## Architecture Patterns
- **Pydantic v2** `BaseModel` for all shapes and resources
- **Auto-generated** resources.py from SageMaker service API definitions
- **Lazy imports** via `__getattr__` to avoid circular dependencies
- **Resource chaining**: resources accept other resources as inputs, auto-extracting attributes
