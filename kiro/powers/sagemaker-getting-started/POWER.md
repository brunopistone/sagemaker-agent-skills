---
name: "sagemaker-getting-started"
displayName: "SageMaker Getting Started"
description: "Plain-language on-ramp for people new to Amazon SageMaker AI and HyperPod: train/deploy models, fine-tune LLMs, classic ML, AutoML, monitoring, prerequisites (IAM/S3/quotas), and instance sizing, with runnable SDK V3 starter code."
keywords:
  [
    "sagemaker",
    "getting started",
    "train a model",
    "fine-tune llm",
    "deploy model",
    "endpoint",
    "qlora",
    "lora",
    "sft",
    "dpo",
    "hyperpod",
    "sagemaker ai",
    "instance sizing",
    "which gpu",
    "iam role",
    "s3",
    "service quota",
    "model monitor",
    "autogluon",
    "automl",
    "sdk v3",
    "modeltrainer",
    "modelbuilder",
  ]
author: "Bruno Pistone"
---

# SageMaker Getting Started

A friendly, self-contained guide for people NEW to Amazon SageMaker. It turns a
vague goal ("I want to fine-tune Llama") into (1) the few prerequisites they
must have, (2) a recommended instance, and (3) runnable, copy-paste code — using
the **SageMaker Python SDK V3**. Only point users to public AWS docs and public
GitHub repos, never to private/local resources.

## What this power does

Guides a newcomer through the full getting-started workflow:

1. Gauge familiarity and capture intent (train / fine-tune / deploy / classic ML / AutoML / monitor).
2. Choose the platform — SageMaker AI managed jobs (default) vs HyperPod; and for HyperPod, Slurm vs EKS.
3. Size the hardware (instance type, sharding) and give rough cost/time.
4. Walk through prerequisites (IAM execution role, S3, region, the specific service quota).
5. Generate complete, runnable SDK V3 code (using the templates under `steering/templates/`).
6. Explain how to run, verify, and — importantly — clean up to stop billing.

Apply the guardrails before writing any code, and prefer the easy managed path
unless scale/duration/resiliency justify HyperPod.

## Onboarding

No Python packages are required to use this power's guidance. When generating code
for the user, the SageMaker Python SDK V3 is installed per task, e.g.:

```bash
pip install sagemaker-core sagemaker-train sagemaker-serve sagemaker-mlops
```

SDK V3 targets Python <= 3.13 (not yet compatible with 3.14+). HyperPod CLI work
uses `pip install sagemaker-hyperpod` (the `hyp` command).

## When to load steering files

Load only the file(s) relevant to the task — do not read all of them upfront.

- **Before writing ANY SageMaker code** (correct-vs-wrong V3 patterns, container choice, CUDA/instance compatibility, pre-delivery checklist) -> `guardrails.md`
- **Choosing SageMaker AI vs HyperPod, managed-job vs cluster, EKS vs Slurm** -> `decision-guide.md`
- **Prerequisites: IAM role, S3, region, quotas, Studio/local setup, cleanup** -> `prerequisites.md`
- **Instance-type tables, memory rules-of-thumb, cost/time, AWS doc links** -> `sizing.md`
- **Serverless model customization (SFT/DPO/RLVR/RLAIF, no infra to manage) — the easiest fine-tuning path** -> `serverless-customization.md`
- **Fine-tuning an LLM via a training job or HyperPod (own script, recipe, or cluster)** -> `llm-finetuning.md`
- **Deploying & invoking an LLM endpoint with V3** -> `llm-inference.md`
- **Training a classic ML model (sklearn/XGBoost/PyTorch) with V3** -> `classic-ml-training.md`
- **Deploying a classic ML model with V3** -> `classic-ml-inference.md`
- **AutoML on tabular/time-series/multimodal data (AutoGluon)** -> `automl-autogluon.md`
- **Monitoring a deployed model (data/model quality, bias, attribution drift)** -> `model-monitor.md`
- **Job governance: queue/prioritize/fair-share training jobs across teams (AWS Batch)** -> `job-governance.md`
- **HyperPod overview: when to use it, Slurm vs EKS, prerequisites, recipes** -> `hyperpod.md`
- **HyperPod `hyp` CLI + SDK: install, cluster/training/inference commands & code** -> `hyperpod-cli-reference.md`
- **Ready-to-adapt runnable code** -> `templates/`

## Notes

This is the onboarding/sizing/decision layer for newcomers. Companion reference
powers, if installed, go deeper on the SDK V3 API and the HyperPod `hyp` CLI —
defer to them for exact APIs or debugging non-trivial existing code.
