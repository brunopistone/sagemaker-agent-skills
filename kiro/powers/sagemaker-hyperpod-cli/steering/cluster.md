# Cluster: Stacks (CloudFormation) & Helm Operators

Two related concerns: **provisioning** cluster infrastructure (CloudFormation, via `HpClusterStack`) and **operating** an existing cluster (kube context, capacity, monitoring, via the top-level `cluster` commands). Note: cluster infra is CFN-backed, unlike the K8s-CRD domains.

## HpClusterStack (CloudFormation) — `cluster_management/hp_cluster_stack.py`

Subclasses `ClusterStackBase` (the 50+ field config in `hyperpod-cluster-stack-template`). Adds `stack_id` / `stack_name`.

| Method                                                                | Kind         | Notes                                                                                                                                                                                                                                   |
| --------------------------------------------------------------------- | ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `create(region=None, template_version=1)`                             | instance     | Builds CFN params from the model, uploads via `TemplateURL` (template hosted in `aws-sagemaker-hyperpod-cluster-setup` S3 bucket per region/stage), returns the describe response. Capabilities: `CAPABILITY_AUTO_EXPAND/IAM/NAMED_IAM` |
| `get_template()`                                                      | staticmethod | Returns `creation_template.yaml` from the template pkg as JSON                                                                                                                                                                          |
| `describe(stack_name, region=None)`                                   | staticmethod | `cf.describe_stacks`                                                                                                                                                                                                                    |
| `list(region=None, stack_status_filter=None)`                         | staticmethod | Paginated; **excludes `DELETE_COMPLETE`** by default to avoid throttling on huge histories                                                                                                                                              |
| `get_status(region=None)`                                             | instance     | Status of `self.stack_name` (must `create()` first)                                                                                                                                                                                     |
| `check_status(stack_name, region=None)`                               | staticmethod | Status of any stack                                                                                                                                                                                                                     |
| `delete(stack_name, region=None, retain_resources=None, logger=None)` | staticmethod | Auto-confirms; handles termination-protection & `retain_resources` (DELETE_FAILED only) errors                                                                                                                                          |

Param building: `_create_parameters()` maps snake_case fields → PascalCase CFN keys (`_snake_to_pascal`, with explicit mappings like `eks_cluster_name`→`EKSClusterName`, `vpc_cidr`→`VpcCIDR`). `instance_group_settings` and `rig_settings` (restricted instance groups) become numbered params `InstanceGroupSettings1..N` / `RigSettings1..N`; list fields (subnets, AZs, security groups) become comma-separated; `tags` become JSON.

```python
from sagemaker.hyperpod.cluster_management.hp_cluster_stack import HpClusterStack
stack = HpClusterStack(resource_name_prefix="demo", ...)   # ClusterStackBase fields
resp = stack.create(region="us-west-2")
print(stack.get_status())
HpClusterStack.list(region="us-west-2")
HpClusterStack.delete("HyperpodClusterStack-abcde", region="us-west-2")
```

## Cluster operation commands — `cli/commands/cluster.py` & `cluster_stack.py`

```bash
# stack lifecycle (cluster_stack.py)
hyp list cluster-stack [--region ...] [--status ...]
hyp describe cluster-stack --stack-name <n>
hyp delete cluster-stack --stack-name <n> [--retain-resources ...]
hyp update cluster ...                       # update_cluster: update an existing HyperPod cluster
# top-level cluster ops (cluster.py)
hyp list-cluster [--region ...] [--output JSON|TABLE] [--clusters ...] [-n <ns>]
hyp set-cluster-context --cluster-name <n>   # updates kubeconfig to point at the EKS cluster
hyp get-cluster-context
hyp get-monitoring                            # observability addon config
```

`list-cluster` enriches output with health labels (`HP_HEALTH_STATUS_LABEL`, `DEEP_HEALTH_CHECK_STATUS_LABEL`), accelerator capacity, and SageMaker-managed queue info; it uses `sagemaker_core.main.resources.Cluster` plus the `KubernetesClient`. Creating a stack is done through the `hyp init cluster-stack` → `hyp create` flow (the standalone `create cluster-stack` command is **not registered** in `hyp_cli.py`).

## Helm Chart — `helm_chart/HyperPodHelmChart`

Deployed into the EKS cluster during stack creation (the `ClusterStackBase` model carries `helm_repo_url`, `helm_repo_path`, `helm_release`, `helm_operators`). Umbrella chart with sub-charts under `charts/`:

`training-operators`, `inference-operator`, `cluster-role-and-bindings`, `namespaced-role-and-bindings`, `team-role-and-bindings`, `deep-health-check`, `health-monitoring-agent`, `hyperpod-patching`, `job-auto-restart`, `mlflow`, `mpi-operator`, `neuron-device-plugin`, `gpu-operator`, `storage` (plus external deps like cert-manager / NVIDIA / EFA device plugins pulled in as dependencies).

`regional-values/` holds ~18 per-region override files (e.g. `values-us-east-1.yaml`) selecting region-correct ECR image URIs for the operators/plugins.
