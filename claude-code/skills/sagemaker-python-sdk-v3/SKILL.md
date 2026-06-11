---
name: sagemaker-python-sdk-v3
description: Deep API REFERENCE for the SageMaker Python SDK V3 (sagemaker-core, sagemaker-train, sagemaker-serve, sagemaker-mlops). Use when writing, reviewing, debugging, or explaining non-trivial code that uses ModelTrainer, ModelBuilder, Pipeline/mlops, SageMaker resources/endpoints, experiments, lineage, JumpStart, remote functions, fine-tuning (SFT/DPO/RLVR/RLAIF), V2-to-V3 migration, or any sagemaker.* imports — i.e. when you need exact classes, params, imports, or lifecycle methods. (This is the deep API-reference layer; for a plain-language getting-started walkthrough, prerequisites, or instance sizing aimed at newcomers, a companion getting-started skill may be installed.)
---

# SageMaker Python SDK V3

V3 is a modular rewrite split into 4 PyPI sub-packages under the `sagemaker.*` namespace. The metapackage `sagemaker` (v3.12.0) depends on all four.

## Quick Reference

| Attribute             | Value                                                                        |
| --------------------- | ---------------------------------------------------------------------------- |
| **Version**           | 3.12.0                                                                       |
| **Python**            | 3.9, 3.10, 3.11, 3.12                                                        |
| **Architecture**      | Modular (4 sub-packages)                                                     |
| **Build**             | setuptools via pyproject.toml                                                |
| **Style**             | black (line-length=100)                                                      |
| **Tests**             | pytest + tox                                                                 |
| **Commit Convention** | `feature:`, `fix:`, `breaking:`, `deprecation:`, `change:`, `documentation:` |

## Dependency Graph

```
sagemaker (metapackage v3.12.0)
  |-- sagemaker-core  >= 2.12.0  (foundation: resources, config, workflow primitives)
  |-- sagemaker-train >= 1.12.0  (depends on: core)
  |-- sagemaker-serve >= 1.12.0  (depends on: core, train)
  '-- sagemaker-mlops >= 1.12.0  (depends on: core, train, serve)
```

All sub-packages use Python namespace packages (`sagemaker.*`), enabling unified imports like `from sagemaker.train import ModelTrainer`.

## API Levels

Two levels of API for interacting with SageMaker resources:

- **High-level API**: `ModelTrainer`, `Processor`, `ModelBuilder` — handles packaging, defaults, and orchestration
- **Low-level API**: Resource classes in `sagemaker.core.resources` — thin wrappers around SageMaker API calls

All resource classes follow a consistent pattern: `create()`, `get()`, `get_all()`, `delete()`, plus resource-specific methods like `wait()`, `stop()`, `update()`, `invoke()`.

## How to use this Skill (read the right file for the task)

Load only the file(s) relevant to the task at hand — do not read all of them upfront.

| If the task involves...                                                                                                                                   | Read this file     |
| --------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------ |
| Creating/managing TrainingJob, ProcessingJob, Model, Endpoint, EndpointConfig, InferenceComponent; full LLM (vLLM) deployment; resource lifecycle methods | `resources.md`     |
| Foundation primitives, config/defaults system, shapes, JumpStart, remote functions, experiments, lineage, S3 utils, serializers, telemetry/attribution    | `package-core.md`  |
| Training, `ModelTrainer`, fine-tuning (SFT/DPO/RLVR/RLAIF), distributed training (Torchrun/MPI/SMP), evaluation, AI Registry, training configs            | `package-train.md` |
| Deployment, `ModelBuilder`, model servers (TorchServe/Triton/TGI/TEI/DJL/etc.), deployment modes, inference types, Bedrock                                | `package-serve.md` |
| Pipelines, `Pipeline`, steps, pipeline variables, retry policies, triggers, Feature Store                                                                 | `package-mlops.md` |
| Migrating V2 code to V3, finding the V3 equivalent of a V2 class/method, V3-only features                                                                 | `migration.md`     |
| Import patterns, exact file paths in the repo, running tests/lint                                                                                         | `reference.md`     |

Repo layout, when needed, is in `reference.md`.
