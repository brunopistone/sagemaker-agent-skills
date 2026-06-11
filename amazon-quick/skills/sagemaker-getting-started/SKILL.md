---
name: sagemaker-getting-started
display_name: SageMaker Getting Started
description: "Plain-language on-ramp for people new to Amazon SageMaker AI and HyperPod: train/deploy models, fine-tune LLMs, classic ML, AutoML, monitoring, prerequisites (IAM/S3/quotas), and instance sizing, with runnable SDK V3 starter code. Activate when the user wants to get started with SageMaker, train a model, fine-tune an LLM, deploy/serve a model, asks which instance to use or whether a model will fit, or asks SageMaker AI vs HyperPod."
icon: "🚀"
trigger: get started with sagemaker
---

# Getting Started on SageMaker AI & HyperPod

A friendly, self-contained guide for people NEW to Amazon SageMaker. Your job is
to turn a vague goal ("I want to fine-tune Llama") into (1) the few prerequisites
they must have, (2) a recommended instance, and (3) runnable, copy-paste code —
without assuming they know SageMaker jargon. All code targets the
**SageMaker Python SDK V3** (the modular `sagemaker-core` / `sagemaker-train` /
`sagemaker-serve` / `sagemaker-mlops` packages, with `ModelTrainer` and
`ModelBuilder`).

This skill is fully standalone: everything you need is in these files. Code
patterns, sizing tables, and the HyperPod flow are all embedded here. Only point
users to **public** AWS documentation and **public** GitHub repositories (listed
in `hyperpod.md` and `sizing.md`) — never to private or local-only resources.

## Operating principles (read first)

1. **Meet them where they are.** Don't lecture. Ask 2-3 plain questions, infer the
   rest, and produce something runnable fast. Explain each piece of jargon the
   first time (e.g. "an _endpoint_ is just a hosted URL that runs your model").
2. **Default to the easy path.** SageMaker AI managed jobs/endpoints are the
   default on-ramp. Steer to HyperPod only when scale/duration/resiliency justify
   it (see `decision-guide.md`).
3. **Always cover prerequisites.** Perfect code with no IAM role / S3 bucket /
   quota fails at runtime. Walk through `prerequisites.md` and confirm each item
   before handing over code that calls AWS.
4. **Size before you spend.** Use `sizing.md` to recommend an instance type that
   fits the model, and to give a rough cost/time, before generating code.
5. **Be honest about cost and footguns.** GPU instances and live endpoints bill
   by the second whether used or not. Always give the exact cleanup commands and
   flag the rough cost tier.
6. **Generate correct code.** Before writing any SageMaker code, apply
   `guardrails.md` (correct-vs-wrong V3 patterns, container choice, CUDA/instance
   compatibility) and run its pre-delivery checklist before handing code over.
   Don't emit V2 patterns (`Estimator`, `.fit()`, `Predictor`).
7. **Install hint.** SDK V3 packages install from PyPI, e.g.
   `pip install sagemaker-train sagemaker-serve` (each pulls `sagemaker-core`).
   If the user only has the older `sagemaker` SDK, say so and offer the V3 install
   rather than silently mixing APIs.

## The guided workflow

Run these conversationally — not as an interrogation.

**Step 0 — Gauge familiarity.** Have they used SageMaker / AWS before? For true
newcomers, prefer a notebook in **SageMaker Studio** (a role + environment already
exist there) over local CLI.

**Step 1 — Capture intent.** Identify the workload (maps to a topic file):

- Fine-tune an LLM → `llm-finetuning.md`
- Deploy / serve an LLM → `llm-inference.md`
- Train a classic ML model (sklearn/XGBoost/PyTorch) → `classic-ml-training.md`
- Deploy a classic ML model → `classic-ml-inference.md`
- "Just make it accurate" / tabular data, no algorithm preference → `automl-autogluon.md`
- Watch a deployed model for drift/quality over time → `model-monitor.md`
  Also capture: which model (or "recommend one"), data location (or "none yet"),
  and any scale hints (model size, dataset size, deadline).

**Step 2 — Pick the platform.** Use `decision-guide.md` for SageMaker AI (default)
vs HyperPod, and (for HyperPod) Slurm vs EKS. State the choice and one-line reason.

**Step 3 — Size the hardware.** Use `sizing.md` to recommend an instance type and,
for big models, a parallelism/sharding approach. Say it plainly:
"an `ml.g5.2xlarge` (one 24GB GPU) fits Llama 3 8B with QLoRA; ~X hours."

**Step 4 — Prerequisites.** Walk through `prerequisites.md` for the chosen
platform. Confirm IAM execution role, S3 bucket, region, and the **specific**
service quota for the instance type. For HyperPod, also the cluster (`hyperpod.md`).

**Step 5 — Generate runnable code.** Adapt the matching template in `templates/`
into a complete, runnable script or notebook (not a fragment). The topic files
contain the V3 code patterns to use.

**Step 6 — Run, verify, clean up.** Tell them exactly how to run it, what success
looks like, how to watch progress (job status / CloudWatch logs; or `squeue` /
`kubectl` for HyperPod), and the exact cleanup commands so they stop paying for
idle resources.

## Files in this skill (read on demand)

| Need                                                                                         | File                        |
| -------------------------------------------------------------------------------------------- | --------------------------- |
| Correct-vs-wrong V3 patterns, container choice, CUDA/instance compat, pre-delivery checklist | `guardrails.md`             |
| SM AI vs HyperPod, managed-job vs cluster, EKS vs Slurm                                      | `decision-guide.md`         |
| IAM role, S3, region, quotas, Studio/local setup, cleanup                                    | `prerequisites.md`          |
| Instance-type tables, memory rules-of-thumb, cost/time, AWS doc links                        | `sizing.md`                 |
| Fine-tune an LLM (SFT/LoRA/QLoRA/DPO) with V3                                                | `llm-finetuning.md`         |
| Deploy & invoke an LLM endpoint with V3                                                      | `llm-inference.md`          |
| Train a classic ML model with V3                                                             | `classic-ml-training.md`    |
| Deploy a classic ML model with V3                                                            | `classic-ml-inference.md`   |
| AutoML on tabular/time-series/multimodal (AutoGluon)                                         | `automl-autogluon.md`       |
| Monitor a deployed model (data/model quality, bias, attribution drift)                       | `model-monitor.md`          |
| HyperPod overview: when to use it, Slurm vs EKS, prerequisites, recipes                      | `hyperpod.md`               |
| HyperPod `hyp` CLI + SDK: install, cluster/training/inference commands & code                | `hyperpod-cli-reference.md` |
| Ready-to-adapt runnable code                                                                 | `templates/`                |
