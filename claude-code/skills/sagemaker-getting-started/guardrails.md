# Guardrails — generate correct V3 code (read before writing SageMaker code)

Apply these whenever you produce SageMaker code. They prevent the most common
errors: V2-vs-V3 mix-ups, wrong containers, and incompatible CUDA/instance combos.
When a specific value is version-sensitive, say so and verify rather than guess.

## Correct vs. wrong (SDK V3)

| Do                                                                             | Don't                                                    | Why                                                     |
| ------------------------------------------------------------------------------ | -------------------------------------------------------- | ------------------------------------------------------- |
| `from sagemaker.train import ModelTrainer`                                     | `from sagemaker.estimator import Estimator`              | Estimator is the V2 API; V3 uses `ModelTrainer`         |
| `from sagemaker.serve import ModelBuilder`                                     | `from sagemaker.model import Model` (V2)                 | V3 packaging/deploy goes through `ModelBuilder`         |
| `from sagemaker.mlops.workflow import Pipeline`                                | `from sagemaker.workflow.pipeline import Pipeline` (V2)  | Pipelines moved to `sagemaker-mlops` in V3              |
| `from sagemaker.core.helper.session_helper import Session, get_execution_role` | `from sagemaker import Session, get_execution_role` (V2) | V3 session helpers live in `sagemaker-core`             |
| `.train(...)` on a trainer                                                     | `.fit(...)` (V2)                                         | V3 renamed the train entrypoint                         |
| `Endpoint.invoke(...)`                                                         | constructing a `Predictor` (V2)                          | V3 invokes via the `Endpoint` resource                  |
| `InputData(channel_name=..., data_source=...)`                                 | `TrainingInput(...)` (V2)                                | V3 input type                                           |
| `pip install sagemaker-train sagemaker-serve`                                  | assume plain `sagemaker` provides V3                     | V3 ships as modular packages on top of `sagemaker-core` |

If the user clearly has only the older `sagemaker` SDK installed, say so and offer
the V3 install instead of silently mixing APIs. (See the migration mapping in
`llm-finetuning.md` / `llm-inference.md` for V2→V3 equivalents.)

## Container decision tree (which image to use)

1. **Text LLM inference (generation/chat)** → a large-model-inference container
   (DJL LMI with a vLLM/TensorRT-LLM backend, or a TGI image). Let `ModelBuilder`
   auto-select when possible; drop to the Core API for specific vLLM env flags.
2. **Embedding model inference** → a TEI (text-embeddings-inference) image.
3. **Classic ML (sklearn / XGBoost)** → the framework Deep Learning Container via
   `image_uris.retrieve(framework="sklearn"|"xgboost", ...)`.
4. **Custom PyTorch / TensorFlow training** → the framework DLC for that version,
   `image_scope="training"`.
5. **Trainium/Inferentia (Neuron)** → a Neuron DLC and an `ml.trn*`/`ml.inf*`
   instance; the toolchain differs from CUDA — don't reuse a GPU image.

Always resolve images with `image_uris.retrieve(...)` rather than hardcoding an
account/registry URI — the correct ECR account differs per region.

## CUDA / instance compatibility (footguns)

- The **container's CUDA version must match the instance GPU's driver.** A
  too-new CUDA build can fail to start on older cards (e.g. very new `cuXXX`
  builds may not run on `ml.g5` A10G nodes due to driver mismatch). When a custom
  image fails to start with a CUDA/driver error, pick an image built for that
  instance family or move to a newer instance.
- Match GPU memory to the model (see `sizing.md`): A10G/L4 = 24 GB, A100 = 40/80 GB,
  H100/H200 = 80/141 GB. Don't put a model that needs >24 GB on a single g5 GPU.
- Inf/Trn (Neuron) require Neuron-compiled artifacts — a CUDA model won't run there.

These specifics change as AWS publishes new DLCs. Verify the current image tag and
its supported instances from the official AWS Deep Learning Containers list before
asserting an exact CUDA version.

## Environment constraint

- The SageMaker Python SDK V3 targets **Python ≤ 3.13** (not yet compatible with
  3.14+). If the user is on 3.14+, have them use a 3.13 (or lower) environment.
- Core deps: `boto3`, plus the V3 packages (`sagemaker-core` and whichever of
  `sagemaker-train` / `sagemaker-serve` / `sagemaker-mlops` the task needs).

## Pre-delivery checklist (run before handing over code)

- [ ] No V2 imports/patterns (no `Estimator`, `.fit()`, `Predictor`, `TrainingInput`).
- [ ] V3 imports come from the right package (`sagemaker.train` / `.serve` /
      `.mlops` / `.core`).
- [ ] Training script saves the model to **`/opt/ml/model/`**; reads inputs from
      `/opt/ml/input/data/<channel>/`.
- [ ] `wait=` is a boolean; instance counts/types are valid SageMaker values.
- [ ] Argparse hyperparameters are typed (e.g. `type=int`), not bare strings.
- [ ] No hardcoded credentials, account IDs, or absolute local machine paths;
      use `get_execution_role()` / `Session()` / `image_uris.retrieve()`.
- [ ] Region is consistent across role, bucket, image, and job.
- [ ] Inference code includes the **cleanup** (delete endpoint/config/model) and a
      cost reminder.
- [ ] For gated models, `HF_TOKEN` / EULA acceptance is handled.
