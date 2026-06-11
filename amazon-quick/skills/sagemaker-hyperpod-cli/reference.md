# Reference: Repo Layout, CLI Tree, Imports, File Locations, Testing

## Repository Layout

```
sagemaker-hyperpod-cli/              # package "sagemaker-hyperpod" v3.8.0
|-- setup.py                         # deps, entry point hyp=...:cli, bundles recipes submodule
|-- pyproject.toml / setup.cfg       # ruff/black/mypy/pytest config (cov-fail-under 50)
|-- README.md                        # large public CLI+SDK usage reference
|-- CHANGELOG.md
|-- src/sagemaker/hyperpod/          # the actual package
|   |-- cli/                         # Click CLI layer
|   |   |-- hyp_cli.py               # main group; wires every subcommand
|   |   |-- commands/                # command impls: training, inference, cluster,
|   |   |   |                        #   cluster_stack, space, space_template, space_access, init
|   |   |-- clients/kubernetes_client.py   # KubernetesClient singleton
|   |   |-- service/                 # per-op K8s helpers (get_logs, list_pods, exec_command, ...)
|   |   |-- validators/              # Validator, ClusterValidator, JobValidator
|   |   |-- constants/               # command_constants, init_constants, space_constants, ...
|   |   |-- training_utils.py / inference_utils.py / space_utils.py   # @generate_click_command
|   |   |-- common_utils.py          # version extraction, load_schema_for_version
|   |   '-- sagemaker_hyperpod_recipes/   # git submodule (NeMo recipes)
|   |-- training/                    # HyperPodPytorchJob SDK + quota/accelerator utils
|   |-- inference/                   # HPEndpoint, HPJumpStartEndpoint, HPEndpointBase + config/
|   |-- cluster_management/          # HpClusterStack + config/
|   |-- space/                       # HPSpace, HPSpaceTemplate + utils
|   |-- observability/               # monitoring config helpers
|   '-- common/                      # config/metadata, telemetry, cli_decorators, utils, exceptions
|-- hyperpod-pytorch-job-template/        # 5 independently-versioned template pip packages
|-- hyperpod-custom-inference-template/   #   (each: registry.py + v1_x/{model,template,schema.json})
|-- hyperpod-jumpstart-inference-template/
|-- hyperpod-cluster-stack-template/
|-- hyperpod-space-template/
|-- helm_chart/HyperPodHelmChart/    # operators/plugins deployed into EKS (see cluster.md)
|-- doc/                             # Sphinx (cli/ + sdk/ reference); .readthedocs.yaml
|-- examples/                        # Jupyter notebooks (training/inference/cluster/observability)
'-- test/                           # unit_tests/ (mocked) + integration_tests/ (live cluster)
```

## The `hyp` Command Tree (from `cli/hyp_cli.py`)

Most actions are **verb groups** with a per-domain **noun** subcommand. Groups use a custom `CLICommand` class; `create` has a hidden `_default_create` for the init flow.

```
hyp init|configure|validate|reset          # init experience (see templates-and-init.md)
hyp create   hyp-pytorch-job | hyp-jumpstart-endpoint | hyp-custom-endpoint
             | hyp-space | hyp-space-template | hyp-space-access
hyp list     hyp-pytorch-job | hyp-recipe-job | hyp-jumpstart-endpoint | hyp-custom-endpoint
             | cluster-stack | hyp-space | hyp-space-template
hyp describe hyp-pytorch-job | hyp-recipe-job | hyp-jumpstart-endpoint | hyp-custom-endpoint
             | cluster-stack | cluster | hyp-space | hyp-space-template
hyp update   cluster | hyp-space | hyp-space-template
hyp delete   hyp-pytorch-job | hyp-recipe-job | hyp-jumpstart-endpoint | hyp-custom-endpoint
             | cluster-stack | hyp-space | hyp-space-template
hyp start|stop   hyp-space
hyp portforward  hyp-space
hyp list-pods    hyp-pytorch-job | hyp-recipe-job | hyp-jumpstart-endpoint | hyp-custom-endpoint
hyp get-logs     hyp-pytorch-job | hyp-recipe-job | hyp-jumpstart-endpoint | hyp-custom-endpoint | hyp-space
hyp get-operator-logs  hyp-pytorch-job | hyp-recipe-job | hyp-jumpstart-endpoint | hyp-custom-endpoint
hyp exec         hyp-pytorch-job | hyp-recipe-job
hyp invoke       hyp-custom-endpoint | hyp-jumpstart-endpoint
# top-level (no noun):
hyp list-cluster | set-cluster-context | get-cluster-context | get-monitoring
hyp list-accelerator-partition-type --instance-type <...>
hyp --version
```

Note: `hyp-recipe-job` commands are `copy.copy()` of the pytorch-job commands with different help text. The `create cluster-stack` command is implemented but **not registered** (`create_cluster_stack` is commented out in `hyp_cli.py`); cluster stacks are created via the `hyp init`/`hyp create` flow.

## Common SDK Import Patterns

```python
# Training
from sagemaker.hyperpod.training.hyperpod_pytorch_job import HyperPodPytorchJob, list_accelerator_partition_types
from sagemaker.hyperpod.common.config import Metadata

# Inference
from sagemaker.hyperpod.inference.hp_jumpstart_endpoint import HPJumpStartEndpoint
from sagemaker.hyperpod.inference.hp_endpoint import HPEndpoint

# Cluster
from sagemaker.hyperpod.cluster_management.hp_cluster_stack import HpClusterStack

# Space
from sagemaker.hyperpod.space.hyperpod_space import HPSpace
from hyperpod_space_template.v1_0.model import SpaceConfig

# Flat config models live in the template packages (used internally by the CLI):
from hyperpod_pytorch_job_template.registry import SCHEMA_REGISTRY  # version -> PyTorchJobConfig
```

## Key File Locations (Quick Lookup)

| What                               | Path                                                                                        |
| ---------------------------------- | ------------------------------------------------------------------------------------------- |
| CLI main group / wiring            | `src/sagemaker/hyperpod/cli/hyp_cli.py`                                                     |
| Training commands                  | `src/sagemaker/hyperpod/cli/commands/training.py`                                           |
| Inference commands                 | `src/sagemaker/hyperpod/cli/commands/inference.py`                                          |
| Cluster commands                   | `src/sagemaker/hyperpod/cli/commands/cluster.py`                                            |
| Cluster-stack commands             | `src/sagemaker/hyperpod/cli/commands/cluster_stack.py`                                      |
| Space / template / access commands | `src/sagemaker/hyperpod/cli/commands/space*.py`                                             |
| Init commands                      | `src/sagemaker/hyperpod/cli/commands/init.py`                                               |
| HyperPodPytorchJob SDK             | `src/sagemaker/hyperpod/training/hyperpod_pytorch_job.py`                                   |
| Quota / accelerator util           | `src/sagemaker/hyperpod/training/quota_allocation_util.py`, `accelerator_partition_util.py` |
| Inference SDK                      | `src/sagemaker/hyperpod/inference/hp_{endpoint,jumpstart_endpoint,endpoint_base}.py`        |
| Cluster stack SDK                  | `src/sagemaker/hyperpod/cluster_management/hp_cluster_stack.py`                             |
| Space SDK                          | `src/sagemaker/hyperpod/space/hyperpod_space.py`, `hyperpod_space_template.py`              |
| K8s client singleton               | `src/sagemaker/hyperpod/cli/clients/kubernetes_client.py`                                   |
| CLI option generators              | `src/sagemaker/hyperpod/cli/{training,inference,space}_utils.py`                            |
| Template wiring (noun→registry)    | `src/sagemaker/hyperpod/cli/constants/init_constants.py`                                    |
| Error-handling decorator           | `src/sagemaker/hyperpod/common/cli_decorators.py`                                           |
| Telemetry decorator                | `src/sagemaker/hyperpod/common/telemetry/telemetry_logging.py`                              |
| Metadata model                     | `src/sagemaker/hyperpod/common/config/metadata.py`                                          |
| Template packages                  | `hyperpod-*-template/hyperpod_*_template/registry.py` + `v1_x/`                             |
| Helm chart                         | `helm_chart/HyperPodHelmChart/`                                                             |

## Testing

```bash
# Unit tests (mocked AWS/K8s)
pytest test/unit_tests
# Integration tests (require AWS creds + a live HyperPod/EKS cluster)
pytest test/integration_tests
# Via tox (py38..py311 envs)
tox
```

`test/conftest.py` ensures the cluster-stack template package is installed before collection and provides class-scoped fixtures (`pytorch_job`, `cluster_name` via `hyp list-cluster`, UUID job names). Coverage gate is 50% (`setup.cfg`).

## CI & Submodule

- CI runs on **AWS CodeBuild**, orchestrated by GitHub Actions (`.github/workflows/codebuild-ci.yml`) with a **collaborator-approval gate** for non-collaborator PRs. Unit tests run on py3.9/3.10/3.11; integration tests on py3.11. A daily `security-monitoring.yml` publishes Dependabot/code-scanning metrics to CloudWatch.
- **Submodule**: `src/sagemaker/hyperpod/cli/sagemaker_hyperpod_recipes` → `github.com/aws/sagemaker-hyperpod-recipes` branch `release-1.3.3` (NeMo-based training recipes; powers `hyp-recipe-job`). `setup.py` runs `git submodule update --init --recursive --remote` and bundles it as data files.
