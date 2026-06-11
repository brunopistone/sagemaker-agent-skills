---
name: "sagemaker-python-sdk-v3"
displayName: "SageMaker Python SDK V3 Reference"
description: "Deep API reference for the SageMaker Python SDK V3 (sagemaker-core, sagemaker-train, sagemaker-serve, sagemaker-mlops): ModelTrainer, ModelBuilder, Pipelines, resources/endpoints, experiments, lineage, JumpStart, fine-tuning, and V2-to-V3 migration."
keywords:
  [
    "sagemaker python sdk",
    "sdk v3",
    "sagemaker-core",
    "sagemaker-train",
    "sagemaker-serve",
    "sagemaker-mlops",
    "modeltrainer",
    "modelbuilder",
    "pipeline",
    "endpoint",
    "trainingjob",
    "jumpstart",
    "lineage",
    "experiments",
    "sft",
    "dpo",
    "rlvr",
    "rlaif",
    "v2 to v3 migration",
    "sagemaker imports",
  ]
author: "Bruno Pistone"
---

# SageMaker Python SDK V3 Reference

V3 is a modular rewrite split into 4 PyPI sub-packages under the `sagemaker.*`
namespace. The metapackage `sagemaker` (v3.12.0) depends on all four:

```
sagemaker (metapackage v3.12.0)
  |-- sagemaker-core  >= 2.12.0  (foundation: resources, config, workflow primitives)
  |-- sagemaker-train >= 1.12.0  (depends on: core)
  |-- sagemaker-serve >= 1.12.0  (depends on: core, train)
  '-- sagemaker-mlops >= 1.12.0  (depends on: core, train, serve)
```

## What this power does

Provides exact, code-level reference for writing/reviewing/debugging SDK V3 code:
class names, parameters, imports, and resource lifecycle methods across training,
deployment, pipelines, and the foundation layer. Two API levels: high-level
(`ModelTrainer`, `Processor`, `ModelBuilder`) and low-level resource classes in
`sagemaker.core.resources` (`create()`/`get()`/`get_all()`/`delete()` + resource
methods like `wait()`/`stop()`/`update()`/`invoke()`).

## Onboarding

Install only what a task needs (Python 3.9-3.12):

```bash
pip install sagemaker-core sagemaker-train sagemaker-serve sagemaker-mlops
```

## When to load steering files

Load only the file(s) relevant to the task — do not read all of them upfront.

- **TrainingJob/ProcessingJob/Model/Endpoint/EndpointConfig/InferenceComponent, full LLM (vLLM) deployment, resource lifecycle methods** -> `resources.md`
- **Foundation primitives, config/defaults system, shapes, JumpStart, remote functions, experiments, lineage, S3 utils, serializers, telemetry/attribution** -> `package-core.md`
- **Training, `ModelTrainer`, fine-tuning (SFT/DPO/RLVR/RLAIF), distributed training (Torchrun/MPI/SMP), evaluation, AI Registry, training configs** -> `package-train.md`
- **Deployment, `ModelBuilder`, model servers (TorchServe/Triton/TGI/TEI/DJL/etc.), deployment modes, inference types, Bedrock** -> `package-serve.md`
- **Pipelines, `Pipeline`, steps, pipeline variables, retry policies, triggers, Feature Store** -> `package-mlops.md`
- **Migrating V2 code to V3, finding the V3 equivalent of a V2 class/method, V3-only features** -> `migration.md`
- **Import patterns, exact file paths, running tests/lint, repo layout** -> `reference.md`

## Notes

This is the deep API-reference layer. For a plain-language getting-started
walkthrough, prerequisites, or instance sizing aimed at newcomers, a companion
getting-started power may be installed.
