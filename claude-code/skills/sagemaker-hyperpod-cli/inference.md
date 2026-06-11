# Inference: JumpStart & Custom Endpoints

Two SDK classes, both subclassing **`HPEndpointBase`** (`src/sagemaker/hyperpod/inference/hp_endpoint_base.py`):

| Class                 | File                                 | CLI noun                 | CRD kind                  |
| --------------------- | ------------------------------------ | ------------------------ | ------------------------- |
| `HPJumpStartEndpoint` | `inference/hp_jumpstart_endpoint.py` | `hyp-jumpstart-endpoint` | `JumpStartModel`          |
| `HPEndpoint`          | `inference/hp_endpoint.py`           | `hyp-custom-endpoint`    | `InferenceEndpointConfig` |

Both create an EKS CRD; the HyperPod **inference operator** (namespace `hyperpod-inference-operator-system`) reconciles it into a real SageMaker endpoint. Constants (group, API version, `KIND_PLURAL_MAP`, `OPERATOR_NAMESPACE`) live in `inference/config/constants.py`.

## HPEndpointBase — shared K8s API layer

| Method                                               | Purpose                 |
| ---------------------------------------------------- | ----------------------- |
| `call_create_api(metadata, kind, spec, debug=False)` | POST the CRD            |
| `call_list_api(kind, namespace)`                     | list CRDs               |
| `call_get_api(name, kind, namespace)`                | get one                 |
| `call_delete_api(name, kind, namespace)`             | delete one              |
| `get_logs(pod, container=None, namespace=None)`      | pod logs                |
| `get_operator_logs(since_hours)`                     | inference-operator logs |
| `list_pods(namespace=None)` / `list_namespaces()`    | pod/namespace listing   |

The subclasses expose lifecycle methods used by the CLI: `create(debug=False)`, `create_from_dict(...)`, `list(namespace)`, `get(name, namespace)`, `delete()`, `refresh()`. The CLI frequently uses `Class.model_construct()` to get an instance without full validation before calling `.list()`/`.get()`.

## Model Sources & Config (custom endpoints)

The custom flat model (`FlatHPEndpoint`, in `hyperpod-custom-inference-template`) supports model-source types: **`s3`**, **`fsx`**, **`huggingface`**, **`kubernetesVolume`**. Notable config groups: storage (`s3_bucket_name`/`s3_region`, `fsx_dns_name`/`fsx_file_system_id`/`fsx_mount_name`), worker (`image_uri`, `container_port`, `model_volume_mount_*`, `resources_requests`/`resources_limits`), TLS (`tls_certificate_output_s3_uri`), and autoscaling (CloudWatch trigger: `metric_name`, `metric_type`, `metric_stat`, `target_value`, `dimensions`, ...). JumpStart endpoints (`FlatHPJumpStartEndpoint`) key off `model_id`, `model_version`, `accept_eula`, `instance_type`.

## CLI Usage

```bash
# Flags generated from the inference template schema (default --version 1.2)
hyp create hyp-jumpstart-endpoint --model-id <id> --instance-type ml.g5.8xlarge --endpoint-name my-js
hyp create hyp-custom-endpoint   --endpoint-name my-cust --instance-type ml.g5.8xlarge \
    --model-source-type s3 --s3-bucket-name <b> --s3-region us-west-2 --image-uri <ecr> ...

hyp list     hyp-jumpstart-endpoint -n default          # tabulated name/namespace/status
hyp describe hyp-custom-endpoint --name my-cust [--full]
hyp list-pods hyp-jumpstart-endpoint --endpoint-name my-js
hyp get-logs  hyp-custom-endpoint --pod-name <pod> [--container <c>]
hyp get-operator-logs hyp-jumpstart-endpoint --since-hours 1
hyp invoke    hyp-custom-endpoint --endpoint-name my-cust --body '{"inputs":"hello"}'
hyp delete    hyp-jumpstart-endpoint --name my-js
```

### Invoke specifics (`inference.py::custom_invoke`)

`--body` must be valid JSON. It resolves the SageMaker `Endpoint` via `sagemaker_core.resources.Endpoint.get`, errors clearly if the endpoint exists but isn't `InService`, or if only the HP CRD exists but the SageMaker endpoint isn't created yet. Then calls `sagemaker-runtime.invoke_endpoint`. Both custom and jumpstart share this impl (jumpstart is a `copy.copy`).

## SDK Usage

```python
from sagemaker.hyperpod.inference.hp_jumpstart_endpoint import HPJumpStartEndpoint
from sagemaker.hyperpod.inference.hp_endpoint import HPEndpoint

ep = HPJumpStartEndpoint(...)        # or build via the template flat model .to_domain()
ep.create(debug=True)

endpoints = HPJumpStartEndpoint.model_construct().list("default")
one = HPEndpoint.model_construct().get("my-cust", "default")
one.delete()
```
