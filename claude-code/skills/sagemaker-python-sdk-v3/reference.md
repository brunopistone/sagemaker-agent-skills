# Reference: Repo Layout, Imports, File Locations, Testing

## Repository Layout

```
sagemaker-python-sdk/           # Root metapackage (version 3.12.0)
|-- pyproject.toml              # Metapackage: depends on all 4 sub-packages
|-- VERSION                     # "3.12.0"
|-- migration.md                # V2 -> V3 migration guide (comprehensive)
|-- README.rst                  # Public-facing README
|-- CONTRIBUTING.md             # Dev guidelines, PR process, commit conventions
|-- CHANGELOG.md                # Full changelog
|
|-- sagemaker-core/             # Foundation package (sagemaker-core on PyPI)
|   |-- pyproject.toml          # Version from sagemaker.core._version.__version__
|   |-- src/sagemaker/core/     # 281 Python files, 46 directories
|   |-- src/sagemaker/lineage/  # Lineage tracking (deprecated shim → sagemaker.core.lineage)
|   |-- tests/                  # unit/ and integ/ tests
|   '-- workflow_helper/        # Workflow helper utilities
|
|-- sagemaker-train/            # Training package (sagemaker-train on PyPI)
|   |-- pyproject.toml          # Depends on sagemaker-core>=2.12.0
|   |-- src/sagemaker/train/    # ModelTrainer + fine-tuning trainers
|   |-- src/sagemaker/ai_registry/ # AI Registry Hub (datasets, evaluators)
|   '-- tests/                  # unit/ and integ/ tests
|
|-- sagemaker-serve/            # Serving package (sagemaker-serve on PyPI)
|   |-- pyproject.toml          # Depends on sagemaker-core + sagemaker-train
|   |-- src/sagemaker/serve/    # ModelBuilder + model servers
|   '-- tests/                  # unit/ and integ/ tests
|
|-- sagemaker-mlops/            # MLOps package (sagemaker-mlops on PyPI)
|   |-- pyproject.toml          # Depends on core + train + serve
|   |-- src/sagemaker/mlops/    # Pipeline, Steps, Local execution
|   '-- tests/                  # unit/ and integ/ tests
|
|-- v3-examples/                # Example notebooks
|   |-- sagemaker_v3_setup.ipynb
|   |-- training-examples/      # 7 notebooks
|   |-- inference-examples/     # 9 notebooks
|   |-- ml-ops-examples/        # 15 notebooks
|   '-- model-customization-examples/ # 11 notebooks (SFT, DPO, RLAIF, RLVR, Nova)
|
|-- docs/                       # Sphinx documentation
|   |-- conf.py, index.rst
|   |-- overview.rst, quickstart.rst, installation.rst
|   |-- training/, inference/, ml_ops/, model_customization/, sagemaker_core/
|   '-- api/                    # API reference docs
|
'-- requirements/               # extras/, tox/
```

## Common Import Patterns

```python
# Training
from sagemaker.train import ModelTrainer, SFTTrainer, DPOTrainer
from sagemaker.train.configs import SourceCode, Compute, InputData, Networking, StoppingCondition
from sagemaker.train.distributed import Torchrun, MPI, SMP
from sagemaker.train import Mode

# Inference
from sagemaker.serve import ModelBuilder
from sagemaker.serve.spec.inference_spec import InferenceSpec
from sagemaker.serve.builder.schema_builder import SchemaBuilder
from sagemaker.serve.utils.types import ModelServer

# MLOps
from sagemaker.mlops.workflow import Pipeline, TrainingStep, ProcessingStep, ModelStep, ConditionStep

# Core
from sagemaker.core.helper.session_helper import Session, get_execution_role
from sagemaker.core import image_uris
from sagemaker.core.resources import TrainingJob, Model, Endpoint, ModelPackage

# Evaluation
from sagemaker.train.evaluate import BenchMarkEvaluator, LLMAsJudgeEvaluator

# AI Registry
from sagemaker.ai_registry import AIRHub, DataSet, Evaluator

# Feature Store
from sagemaker.mlops.feature_store import FeatureGroupManager, DatasetBuilder, FeatureDefinition

# Telemetry/Attribution
from sagemaker.core import Attribution, set_attribution

# Training Observability
from sagemaker.train import plot_training_metrics, get_available_metrics
```

## Testing

```bash
# Unit tests for a specific sub-package
cd sagemaker-train && tox tests/unit

# Single test
tox -e py310 -- -s -vv tests/unit/train/test_model_trainer.py::test_function_name

# Lint
tox -e flake8,pylint,docstyle,black-check,twine --parallel all
```

### Test Organization (per sub-package)

```
tests/
  unit/          # Mocked tests, no AWS calls
  integ/         # Integration tests requiring AWS credentials
```

## Key File Locations (Quick Lookup)

| What                         | Path                                                                     |
| ---------------------------- | ------------------------------------------------------------------------ |
| ModelTrainer implementation  | `sagemaker-train/src/sagemaker/train/model_trainer.py`                   |
| ModelTrainer configs         | `sagemaker-core/src/sagemaker/core/training/configs.py`                  |
| SFT/DPO/RLVR/RLAIF trainers  | `sagemaker-train/src/sagemaker/train/{sft,dpo,rlvr,rlaif}_trainer.py`    |
| ModelBuilder implementation  | `sagemaker-serve/src/sagemaker/serve/model_builder.py`                   |
| InferenceSpec                | `sagemaker-serve/src/sagemaker/serve/spec/inference_spec.py`             |
| Pipeline implementation      | `sagemaker-mlops/src/sagemaker/mlops/workflow/pipeline.py`               |
| Step definitions             | `sagemaker-mlops/src/sagemaker/mlops/workflow/steps.py`                  |
| Processing jobs (high-level) | `sagemaker-core/src/sagemaker/core/processing.py`                        |
| Spark processing             | `sagemaker-core/src/sagemaker/core/spark/processing.py`                  |
| Generated resources          | `sagemaker-core/src/sagemaker/core/resources.py`                         |
| Generated shapes             | `sagemaker-core/src/sagemaker/core/shapes/shapes.py`                     |
| Config schema                | `sagemaker-core/src/sagemaker/core/config/config_schema.py`              |
| Image URI configs            | `sagemaker-core/src/sagemaker/core/image_uri_config/*.json`              |
| JumpStart module             | `sagemaker-core/src/sagemaker/core/jumpstart/`                           |
| Workflow primitives          | `sagemaker-core/src/sagemaker/core/workflow/`                            |
| Remote function              | `sagemaker-core/src/sagemaker/core/remote_function/`                     |
| Container drivers            | `sagemaker-train/src/sagemaker/train/container_drivers/`                 |
| Local training               | `sagemaker-train/src/sagemaker/train/local/`                             |
| Local inference              | `sagemaker-serve/src/sagemaker/serve/mode/`                              |
| Local pipelines              | `sagemaker-mlops/src/sagemaker/mlops/local/`                             |
| Evaluation framework         | `sagemaker-train/src/sagemaker/train/evaluate/`                          |
| AI Registry                  | `sagemaker-train/src/sagemaker/ai_registry/`                             |
| Token generator              | `sagemaker-core/src/sagemaker/core/token_generator/`                     |
| Attribution/telemetry        | `sagemaker-core/src/sagemaker/core/telemetry/attribution.py`             |
| Feature Store                | `sagemaker-mlops/src/sagemaker/mlops/feature_store/`                     |
| Metrics visualizer           | `sagemaker-train/src/sagemaker/train/common_utils/metrics_visualizer.py` |
| Training enums               | `sagemaker-train/src/sagemaker/train/common.py`                          |
| V3 examples                  | `v3-examples/`                                                           |
| Migration guide              | `migration.md`                                                           |
