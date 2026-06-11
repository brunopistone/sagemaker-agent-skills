# Dev Spaces

Interactive JupyterLab/IDE development workspaces on a HyperPod cluster.

| Class | File | CLI noun |
|-------|------|----------|
| `HPSpace` | `src/sagemaker/hyperpod/space/hyperpod_space.py` | `hyp-space` |
| `HPSpaceTemplate` | `src/sagemaker/hyperpod/space/hyperpod_space_template.py` | `hyp-space-template` |
| (space access on `HPSpace`) | — | `hyp-space-access` |

**Backed by:** K8s CRDs in the `workspace.jupyter.org` family. Constants in `cli/constants/space_constants.py` (`SPACE_GROUP`, `SPACE_VERSION`, `SPACE_PLURAL`, `DEFAULT_SPACE_PORT`) and `space_access_constants.py`. Config model `SpaceConfig` (+ `ResourceRequirements`) lives in `hyperpod-space-template/hyperpod_space_template/v1_0/model.py` (single version, `1.0`).

`HPSpace` is a `BaseModel` holding `config: SpaceConfig` and `raw_resource` (the full K8s object). Properties `api_version`/`kind`/`metadata`/`status` read from `raw_resource`.

## HPSpace Methods

| Method | Notes |
|--------|-------|
| `create(debug=False)` | Validates MIG profiles, `config.to_domain()` → `space_spec`, POSTs CRD |
| `list(namespace=None)` | classmethod; returns only spaces created by the **caller** (matches STS ARN annotation `workspace.jupyter.org/created-by`) **or** `ownershipType == "Public"`; paginated |
| `get(name, namespace=None)` | classmethod |
| `delete()` | |
| `update(**kwargs)` | PATCHes spec; handles MIG profile swaps |
| `start()` / `stop()` | convenience: `update(desired_status="Running"/"Stopped")` |
| `list_pods()` | pods labeled `workspace.jupyter.org/workspace-name=<name>` |
| `get_logs(pod_name=None, container=None)` | default container `workspace` |
| `create_space_access(connection_type="vscode-remote")` | returns `{SpaceConnectionType, SpaceConnectionUrl}`; type must be `web-ui` or match `{ide}-remote` (e.g. `vscode-remote`, `kiro-remote`, `cursor-remote`) |
| `portforward_space(local_port, remote_port=DEFAULT_SPACE_PORT)` | uses `kr8s` `Pod.portforward`; requires space in `Available` status |

MIG handling: `_validate_and_extract_mig_profiles()` enforces a single `nvidia.com/mig-*` profile shared by requests & limits, validated against the cluster (`space/utils.py`).

## CLI Usage

```bash
hyp create hyp-space --name my-space ...           # flags generated from SpaceConfig schema
hyp create hyp-space-template ...                  # reusable space template
hyp create hyp-space-access --name my-space --connection-type vscode-remote

hyp list      hyp-space [-n <ns>]
hyp describe  hyp-space --name my-space
hyp update    hyp-space --name my-space ...
hyp start     hyp-space --name my-space
hyp stop      hyp-space --name my-space
hyp portforward hyp-space --name my-space --local-port 8080
hyp get-logs  hyp-space --name my-space
hyp delete    hyp-space --name my-space
```

## SDK Usage

```python
from sagemaker.hyperpod.space.hyperpod_space import HPSpace
from hyperpod_space_template.v1_0.model import SpaceConfig

space = HPSpace(config=SpaceConfig(name="my-space", namespace="my-ns", ...))
space.create()
space.start()
access = space.create_space_access("vscode-remote")
print(access["SpaceConnectionUrl"])
space.stop(); space.delete()
```
