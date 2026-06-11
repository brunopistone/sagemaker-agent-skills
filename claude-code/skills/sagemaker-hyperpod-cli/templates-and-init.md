# Template Packages, Schema-Driven CLI & the Init Experience

The extensibility backbone of the project. Read this when adding a CLI flag, bumping a schema version, onboarding a new resource type, or explaining where `hyp` options come from.

## The Five Template Packages

Each is a **separate, independently-versioned pip package** living at the repo root, declared as a dependency in the main `setup.py` (`hyperpod-*-template>=1.0.0,<2.0.0`).

| Package                                 | Imported registry         | Versions            | `to_*` method                                                      |
| --------------------------------------- | ------------------------- | ------------------- | ------------------------------------------------------------------ |
| `hyperpod_pytorch_job_template`         | `PyTorchJobConfig`        | `1.0`, `1.1`        | `to_domain()` → `HyperPodPytorchJob`                               |
| `hyperpod_custom_inference_template`    | `FlatHPEndpoint`          | `1.0`, `1.1`, `1.2` | `to_domain()` → `HPEndpoint`                                       |
| `hyperpod_jumpstart_inference_template` | `FlatHPJumpStartEndpoint` | `1.0`, `1.1`, `1.2` | `to_domain()` → `HPJumpStartEndpoint`                              |
| `hyperpod_cluster_stack_template`       | `ClusterStackBase`        | `1.0`               | `to_config()` → `HpClusterStack` (also a `creation_template.yaml`) |
| `hyperpod_space_template`               | `SpaceConfig`             | `1.0`               | `to_domain()` → space spec dict                                    |

### Package internals

Each package's `registry.py` exposes:

```python
SCHEMA_REGISTRY   = {"1.0": <FlatModel v1_0>, "1.1": ...}   # version -> flat Pydantic model class
TEMPLATE_REGISTRY = {"1.0": <jinja string v1_0>, ...}        # version -> Jinja2 template (CRD/CFN)
```

and per-version subpackages `v1_0/`, `v1_1/`, ... each holding:

- `model.py` — the **flat** Pydantic model (one level of CLI-friendly fields) with a `to_domain()`/`to_config()` method that expands into the nested SDK/domain object.
- `template.py` — `TEMPLATE_CONTENT`, the Jinja2 template that renders the K8s manifest (CRD) or CloudFormation params (CFN).
- `schema.json` — JSON Schema describing the flat model; used to generate CLI options.

## Schema-Driven CLI: `@generate_click_command`

Three near-identical generators: `cli/training_utils.py`, `cli/inference_utils.py`, `cli/space_utils.py`. Each:

1. Picks the version (`extract_version_from_args` / `get_latest_version`, default = highest registry key, overridable with `--version`).
2. Loads `schema.json` for that version (`load_schema_for_version`, `common_utils.py`) and injects a Click option per property — complex props (`env`, `dimensions`, `resources_limits/requests`, `kubernetes`, `node_affinity`, `tags`, `probes`, `auto_scaling_spec`, ...) are parsed as JSON flags.
3. At invocation: instantiates `Model = registry[version]`, builds `flat = Model(**kwargs)`, then `domain = flat.to_domain()` and calls the command body `func(version, debug, domain)`.

So adding a field to a template package's model + schema.json automatically surfaces a new `hyp` flag — no change to the CLI command code.

## Central Wiring: `init_constants.py`

`cli/constants/init_constants.py::TEMPLATES` maps each noun to its registry, template registry, schema package, schema type (`"crd"` or `"cfn"`), and rendering `"type"` (`"jinja"`, or `"dynamic"` for `hyp-recipe-job`):

```python
TEMPLATES = {
  "hyp-jumpstart-endpoint": {... schema_type: "crd", type: "jinja"},
  "hyp-custom-endpoint":    {... schema_type: "crd", type: "jinja"},
  "hyp-pytorch-job":        {... schema_type: "crd", type: "jinja"},
  "cluster-stack":          {... schema_type: "cfn", type: "jinja"},
  "hyp-recipe-job":         {registry: {}, schema_pkg: None, schema_type: "crd", type: "dynamic"},
}
```

Also here: `K8S_KIND_MAPPING` (CRD kind → SDK class path, for `create_from_k8s_yaml`) and `SPECIAL_FIELD_HANDLERS` (e.g. `hyp-pytorch-job.1.0.volume` → a `VOLUME_TYPE_HANDLER` imported dynamically from the versioned model module, for custom volume parsing/rendering).

## The `hyp init` Experience

A file-scaffolding workflow distinct from direct `hyp create <noun> --flags`:

```bash
hyp init <template-type> [dir]   # writes config.yaml + (k8s.jinja | cfn_params.jinja) + README.md
hyp configure --field value ...  # edit individual config.yaml fields
hyp validate                     # check config.yaml against the JSON schema
hyp reset                        # restore defaults (keeps template type + namespace)
hyp create                       # (no noun) render template with config.yaml → runs/<ts>/{k8s,cfn_params}.yaml and submit
```

`hyp create` with no subcommand falls through to the hidden `_default_create` (the `CLICommand` group's `default_cmd`), which validates `config.yaml` and renders + deploys. CRD templates render to `k8s.yaml`; cluster-stack renders to `cfn_params.yaml`. Full guide text is in `init_constants.py` (`USAGE_GUIDE_TEXT_CRD` / `USAGE_GUIDE_TEXT_CFN`).

## Onboarding a new resource type (the intended extension path)

1. Create a `hyperpod-<x>-template` package with `registry.py` + `v1_0/{model.py (with to_domain), template.py, schema.json}`.
2. Add it to `TEMPLATES` in `init_constants.py`.
3. Add Click commands that use `@generate_click_command(schema_pkg=..., registry=...)` and call `domain.create()`.
4. Register the commands in `hyp_cli.py` under the relevant verb groups.
