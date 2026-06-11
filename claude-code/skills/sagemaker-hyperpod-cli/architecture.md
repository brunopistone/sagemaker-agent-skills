# Architecture: Cross-Cutting Layers & Data Flow

Read this for the internals shared across all domains: Kubernetes access, error handling, telemetry, metadata, and the end-to-end request trace.

## Layering

```
Click CLI (cli/commands/*)  ──▶  SDK domain classes (training/ inference/ cluster_management/ space/)
                                      │
              ┌───────────────────────┼───────────────────────────────┐
              ▼                       ▼                               ▼
   KubernetesClient singleton   CustomObjectsApi (CRDs)        boto3 / sagemaker-core
   (cli/clients/...)            CoreV1Api (pods/logs/exec)      (CloudFormation, STS, sagemaker-runtime)
```

The CLI is a thin layer: parse flags → build domain object → call an SDK method. SDK classes talk to Kubernetes via the `kubernetes` python client (and `kr8s` for space port-forwarding), or to AWS via boto3/`sagemaker-core`.

## KubernetesClient — `cli/clients/kubernetes_client.py`

Singleton (`_instance`, `__new__`-based). Wraps an `ApiClient` and exposes typed accessors: `get_core_v1_api()`, `get_apps_v1_api()`, `get_auth_v1_api()`, `get_custom_objects_api()`, plus context helpers (`set_context`, `get_current_context_namespace`, namespace existence checks). SDK domain classes mostly call `kubernetes.client.CustomObjectsApi()` directly and load kubeconfig lazily via their own `verify_kube_config()` (guarded by an `is_kubeconfig_loaded` flag + a Kubernetes-version compatibility check).

## Service helpers — `cli/service/`

Reusable operation classes/functions: `list_pods.py`, `get_logs.py`, `exec_command.py`, `get_training_job.py`, `list_training_jobs.py`, `cancel_training_job.py`, `discover_namespaces.py` / `get_namespaces.py`, `self_subject_access_review.py` (RBAC/SSAR permission checks). Used mainly by the cluster/training commands for richer output and access discovery.

## Error handling — `common/cli_decorators.py`

`@handle_cli_exceptions()` wraps almost every CLI command. It detects the operation (create/delete/describe/get-logs) and resource type, proactively validates namespace existence, and turns raw 404s/K8s errors into actionable messages (e.g. suggests `hyp list`, checks the training-operator CRD for pytorch jobs, validates JumpStart model IDs). SDK-level errors funnel through `common/utils.py::handle_exception(e, name, namespace, operation_type=..., resource_type=...)`.

## Telemetry — `common/telemetry/`

`@_hyperpod_telemetry_emitter(Feature.X, "operation_name")` decorates both SDK methods and CLI commands. `Feature.HYPERPOD` is used on SDK methods, `Feature.HYPERPOD_CLI` on CLI commands (constants in `telemetry/constants.py`). It records operation, success/failure, duration, region/account (from kube context), and SDK/python/OS versions. User-agent suffix from `telemetry/user_agent.py`.

## Metadata — `common/config/metadata.py`

`Metadata(BaseModel)`: `name` (RFC1123), `namespace`, `labels`, `annotations`. The standard K8s metadata object attached to training jobs and inference endpoints (`from sagemaker.hyperpod.common.config import Metadata`).

## Validators — `cli/validators/`

`Validator.validate_aws_credential(session)`; `ClusterValidator` (EKS access pre-checks before kubeconfig update); `JobValidator` (job params).

## End-to-End: `hyp create hyp-pytorch-job`

```
hyp create hyp-pytorch-job --job-name j --image i --instance-type ml.g5.8xlarge ...
  │  hyp_cli.py: create group → pytorch_create command
  │  @generate_click_command(schema_pkg="hyperpod_pytorch_job_template", registry=SCHEMA_REGISTRY)
  ▼     loads schema.json (version 1.0 default), injects --flags
flat = PyTorchJobConfig(**kwargs)              # flat Pydantic model from template pkg
domain = flat.to_domain()                       # → HyperPodPytorchJob
  │  @_hyperpod_telemetry_emitter(HYPERPOD_CLI, "create_pytorchjob_cli")
  │  @handle_cli_exceptions()
  ▼
pytorch_create(version, debug, job) → job.create(debug)
  │  HyperPodPytorchJob.create():
  │    verify_kube_config(); allocate_quotas_if_applicable() (quota_allocation_util)
  │    build body {apiVersion: sagemaker.amazonaws.com/v1, kind: HyperPodPyTorchJob, metadata, spec}
  ▼
CustomObjectsApi.create_namespaced_custom_object(group, v1, ns, "hyperpodpytorchjobs", body)
  ▼
EKS: training operator (ns aws-hyperpod) reconciles the CRD → worker pods
```

Inference follows the same shape but ends in `HPEndpointBase.call_create_api` (CRD reconciled by the inference operator); cluster-stack diverges entirely to CloudFormation (`HpClusterStack.create` → `cf.create_stack`).
