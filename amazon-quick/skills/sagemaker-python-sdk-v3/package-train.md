# Package 2: sagemaker-train

**Namespace:** `sagemaker.train` + `sagemaker.ai_registry`
**Role:** Model training, fine-tuning, evaluation, distributed training
**PyPI:** `sagemaker-train` (depends on sagemaker-core>=2.12.0)

## Key Classes

| Class | File | Purpose |
|-------|------|---------|
| **`ModelTrainer`** | `model_trainer.py` | Primary training interface (replaces all V2 Estimators) |
| **`SFTTrainer`** | `sft_trainer.py` | Supervised Fine-Tuning |
| **`DPOTrainer`** | `dpo_trainer.py` | Direct Preference Optimization |
| **`RLVRTrainer`** | `rlvr_trainer.py` | RL from Verifiable Rewards |
| **`RLAIFTrainer`** | `rlaif_trainer.py` | RL from AI Feedback |
| `BaseTrainer` | `base_trainer.py` | Abstract base for all trainers |
| `Torchrun` | `distributed.py` | PyTorch distributed config |
| `MPI` | `distributed.py` | MPI distributed config |
| `SMP` | `distributed.py` | SageMaker Model Parallelism v2 |
| `_LocalContainer` | `local/local_container.py` | Docker-based local training |
| `BenchMarkEvaluator` | `evaluate/benchmark_evaluator.py` | Standard benchmark evaluation |
| `CustomScorerEvaluator` | `evaluate/custom_scorer_evaluator.py` | Custom metric evaluation |
| `LLMAsJudgeEvaluator` | `evaluate/llm_as_judge_evaluator.py` | LLM-based evaluation |
| `AIRHub` | `ai_registry/air_hub.py` | AI Registry Hub client |
| `DataSet` | `ai_registry/dataset.py` | Dataset entity |
| `Evaluator` | `ai_registry/evaluator.py` | Evaluator entity |
| `TrainingQueue` | `aws_batch/training_queue.py` | AWS Batch queue management |
| `TrainingType` | `common.py` | Enum: `LORA`, `FULL` |
| `CustomizationTechnique` | `common.py` | Enum: `SFT`, `RLVR`, `RLAIF`, `DPO` |
| `FineTuningOptions` | `common.py` | Dynamic validated options container for fine-tuning hyperparams |
| `EvaluationPipelineExecution` | `evaluate/` | Evaluation pipeline execution management |

## Configuration Objects (from `sagemaker.core.training.configs`)

| Config | Key Fields |
|--------|-----------|
| `Compute` | `instance_type`, `instance_count`, `volume_size_in_gb`, `enable_managed_spot_training`, `keep_alive_period_in_seconds` |
| `SourceCode` | `source_dir`, `entry_script`, `requirements`, `command`, `ignore_patterns` |
| `Networking` | `subnets`, `security_group_ids`, `enable_network_isolation`, `enable_inter_container_traffic_encryption` |
| `StoppingCondition` | `max_runtime_in_seconds`, `max_wait_time_in_seconds` |
| `InputData` / `Channel` | `channel_name`, `data_source`, `content_type`, `input_mode` |
| `OutputDataConfig` | `s3_uri`, `kms_key_id` |
| `CheckpointConfig` | `s3_uri`, `local_path` |

## ModelTrainer.train() Flow
1. Validates inputs (training_image XOR algorithm_name)
2. Resolves intelligent defaults from config hierarchy
3. Packages source code + container drivers into temp directory
4. Generates `sm_train.sh` entrypoint script
5. Creates S3 input channels (code, drivers, recipe, user data)
6. **Remote mode**: calls `TrainingJob.create()` from sagemaker-core
7. **Local mode**: creates `_LocalContainer` with Docker
8. If `wait=True`: polls status, streams logs
9. Returns `TrainingJob` resource

## Factory Methods
- `ModelTrainer.from_recipe(recipe, ...)` - Load from sagemaker-hyperpod-recipes
- `ModelTrainer.from_jumpstart_config(model_id, ...)` - Create from JumpStart model

## Container Driver Architecture
```
In container at runtime:
/opt/ml/input/data/
  sm_drivers/           # SDK drivers (torchrun_driver.py, mpi_driver.py, etc.)
    sm_train.sh         # Generated entrypoint
    sourcecode.json     # Serialized SourceCode config
    distributed.json    # Serialized distributed config
  code/                 # User's source code
  recipe/               # Training recipe (if using recipes)
  train/                # User training data
```

## Training Modes
- `Mode.SAGEMAKER_TRAINING_JOB` - Remote on SageMaker (default)
- `Mode.LOCAL_CONTAINER` - Local Docker container

## Distributed Training Options
- **Torchrun**: PyTorch distributed (auto-detects GPU count, EFA support)
- **MPI**: MPI-based distribution (SSH daemon, master/worker coordination)
- **SMP v2**: SageMaker Model Parallelism (tensor/context/expert parallel, FSDP)

## Training Observability
- `plot_training_metrics()` / `get_available_metrics()` - MLflow metrics visualization
- `get_studio_url()` / `get_mlflow_url()` - URL helpers for monitoring jobs
- Configurable `poll_interval` parameter on all trainers for job status observability
