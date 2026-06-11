---
name: "sagemaker-hyperpod-cli"
displayName: "SageMaker HyperPod CLI Reference"
description: "Deep code-level reference for the SageMaker HyperPod CLI + SDK (the `hyp` command, package sagemaker-hyperpod, EKS/Kubernetes-orchestrated): training jobs, inference endpoints, cluster stacks, dev spaces, CRDs, schema-driven templates, and quota allocation."
keywords:
  [
    "hyperpod",
    "hyp cli",
    "sagemaker-hyperpod",
    "HyperPodPytorchJob",
    "HPEndpoint",
    "HPJumpStartEndpoint",
    "HpClusterStack",
    "HPSpace",
    "eks",
    "kubernetes",
    "cluster stack",
    "cloudformation",
    "helm",
    "recipe job",
    "hyp-pytorch-job",
    "hyp-custom-endpoint",
    "task governance",
    "quota allocation",
  ]
author: "Bruno Pistone"
---

# SageMaker HyperPod CLI Reference

A Python **CLI + SDK** for managing Amazon SageMaker HyperPod clusters
orchestrated by **Amazon EKS/Kubernetes**. The CLI binary is `hyp`. It abstracts
direct Kubernetes/CloudFormation work for the full lifecycle of training jobs,
inference endpoints, cluster infrastructure, and interactive dev spaces.

## What this power does

Provides code-level reference for the `hyp` CLI and `sagemaker.hyperpod` SDK
across its five domains:

| Domain                | SDK class(es)                | CLI noun(s)                         | Backed by                         |
| --------------------- | ---------------------------- | ----------------------------------- | --------------------------------- |
| Training              | `HyperPodPytorchJob`         | `hyp-pytorch-job`, `hyp-recipe-job` | K8s CRD `HyperPodPyTorchJob`      |
| Inference (JumpStart) | `HPJumpStartEndpoint`        | `hyp-jumpstart-endpoint`            | K8s CRD `JumpStartModel`          |
| Inference (custom)    | `HPEndpoint`                 | `hyp-custom-endpoint`               | K8s CRD `InferenceEndpointConfig` |
| Cluster infra         | `HpClusterStack`             | `cluster-stack`, `cluster`          | CloudFormation + Helm             |
| Dev spaces            | `HPSpace`, `HPSpaceTemplate` | `hyp-space*`                        | K8s CRD                           |

The CLI is **schema-driven**: each domain's config schema lives in a separate
versioned `hyperpod-*-template` package; `hyp` generates its flags dynamically
from those schemas (`CLI flags -> flat Pydantic model -> .to_domain() -> SDK
object -> .create()` against the K8s CRD API or CloudFormation).

## Onboarding

Install the CLI (Python 3.8-3.11). The `hyp` binary becomes available:

```bash
pip install sagemaker-hyperpod
hyp --help
```

Versions, class names, and CLI nouns describe `sagemaker-hyperpod` v3.8.0 and may
shift in later releases — verify against the installed version and `hyp --help`.

## When to load steering files

Load only the file(s) relevant to the task — do not read all of them upfront.

- **`hyp` command tree, SDK imports, key file paths, running tests, CI, the recipes submodule** -> `reference.md`
- **Training jobs: `HyperPodPytorchJob`, `hyp ... hyp-pytorch-job`/`hyp-recipe-job`, GPU/Neuron/EFA resources, accelerator partitions (MIG), quotas, `replica_count`** -> `training.md`
- **Inference: `HPJumpStartEndpoint`/`HPEndpoint`/`HPEndpointBase`, jumpstart vs custom endpoints, model sources (s3/fsx/hf), autoscaling, invoke** -> `inference.md`
- **Cluster provisioning: `HpClusterStack`, `cluster-stack`/`cluster` commands, CloudFormation, the Helm chart and its operators** -> `cluster.md`
- **Dev spaces: `HPSpace`/`HPSpaceTemplate`, `hyp-space*` commands, start/stop/portforward/space-access** -> `space.md`
- **The template packages, registries, `to_domain()`, `@generate_click_command`, `hyp init` experience, versioning** -> `templates-and-init.md`
- **Cross-cutting internals: `KubernetesClient`, service helpers, `@handle_cli_exceptions`, telemetry, `Metadata`, end-to-end data flow** -> `architecture.md`

## Sources

Derived from the public, open-source codebase and official AWS docs:
`github.com/aws/sagemaker-hyperpod-cli` (main branch),
`github.com/aws/sagemaker-hyperpod-recipes`, and the _Amazon SageMaker Developer
Guide_ ("Orchestrating SageMaker HyperPod clusters with Amazon EKS").

## Notes

This is the deep HyperPod CLI/SDK reference layer. For a newcomer's "should I use
HyperPod and how do I get started" walkthrough (incl. Slurm, prerequisites,
HyperPod vs managed jobs), a companion getting-started power may be installed.
