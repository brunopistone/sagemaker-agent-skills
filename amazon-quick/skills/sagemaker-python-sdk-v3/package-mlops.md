# Package 4: sagemaker-mlops

**Namespace:** `sagemaker.mlops`
**Role:** Pipeline orchestration, workflow management
**PyPI:** `sagemaker-mlops` (depends on core + train + serve)

## Key Classes

| Class | File | Purpose |
|-------|------|---------|
| **`Pipeline`** | `workflow/pipeline.py` | Main pipeline definition and execution |
| `PipelineGraph` | `workflow/pipeline.py` | DAG validation and traversal |
| `Step` | `workflow/steps.py` | Base step class |
| `TrainingStep` | `workflow/steps.py` | Training job step |
| `ProcessingStep` | `workflow/steps.py` | Processing job step |
| `TransformStep` | `workflow/steps.py` | Batch transform step |
| `TuningStep` | `workflow/steps.py` | HPO tuning step |
| `ModelStep` | `workflow/model_step.py` | Model creation/registration |
| `ConditionStep` | `workflow/condition_step.py` | Conditional branching |
| `LambdaStep` | `workflow/lambda_step.py` | Lambda invocation |
| `CallbackStep` | `workflow/callback_step.py` | SQS callback step |
| `FailStep` | `workflow/fail_step.py` | Explicit pipeline failure |
| `EMRStep` | `workflow/emr_step.py` | EMR cluster job |
| `EMRServerlessStep` | `workflow/emr_serverless_step.py` | EMR Serverless job |
| `QualityCheckStep` | `workflow/quality_check_step.py` | Data/model quality |
| `ClarifyCheckStep` | `workflow/clarify_check_step.py` | Bias/explainability |
| `NotebookJobStep` | `workflow/notebook_job_step.py` | Notebook execution |
| `AutoMLStep` | `workflow/automl_step.py` | AutoML |
| `FunctionStep` | `workflow/function_step.py` | Pipeline step for arbitrary Python functions |
| `MonitorBatchTransformStep` | `workflow/monitor_batch_transform_step.py` | Quality/Clarify monitoring for batch transform |
| `LocalPipelineSession` | `local/local_pipeline_session.py` | Local pipeline execution |

## Pipeline Usage Pattern
```python
from sagemaker.mlops.workflow import Pipeline, TrainingStep, ModelStep

training_step = TrainingStep(name="train", model_trainer=trainer)
model_step = ModelStep(name="register", depends_on=[training_step])
pipeline = Pipeline(name="my-pipeline", steps=[training_step, model_step])
pipeline.create()
execution = pipeline.start()
execution.wait()
```

## Pipeline Variables (from sagemaker.core.workflow)
- `ParameterString/Integer/Float/Boolean` - Pipeline parameters
- `ExecutionVariables` - Runtime context (PIPELINE_NAME, EXECUTION_ID, etc.)
- `Properties` - Step output references
- `Join`, `JsonGet` - Pipeline functions
- `CallbackOutput`, `LambdaOutput` - Step-specific outputs

## Retry Policies
- `StepRetryPolicy` - SERVICE_FAULT, THROTTLING
- `SageMakerJobStepRetryPolicy` - JOB_INTERNAL_ERROR, CAPACITY_ERROR, RESOURCE_LIMIT

## Triggers
- `PipelineSchedule` - EventBridge-based: `at()`, `rate()`, `cron()`

## Feature Store (`sagemaker.mlops.feature_store`)
- `FeatureGroupManager` - Feature group lifecycle management (Iceberg, Lake Formation)
- `DatasetBuilder` - Build datasets from feature groups
- `FeatureDefinition` - Feature type definitions and collections
- `AthenaQuery` - Query feature data via Athena
- `IngestionManagerPandas` - Ingest DataFrames into feature groups
- Feature processor pipeline with EventBridge scheduling
