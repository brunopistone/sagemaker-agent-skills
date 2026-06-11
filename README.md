# SageMaker Agent Skills

Three complementary capabilities for working with **Amazon SageMaker AI** and
**SageMaker HyperPod** using the **SageMaker Python SDK V3**, packaged for three
AI coding agents:

- **Claude Code** — as Agent Skills (`SKILL.md`)
- **Amazon Quick** — as Quick Skills (`SKILL.md` + `scripts/`)
- **Kiro** — as Kiro Powers (`POWER.md` + `steering/`)

The same knowledge is shipped three ways; pick the folder for your agent.

## The three capabilities

| Capability                    | Lane                    | Use it for                                                                                                                                                                                                         |
| ----------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **sagemaker-getting-started** | On-ramp / guide         | Newcomers. "Get started", fine-tune an LLM, deploy a model, classic ML, AutoML, monitoring, prerequisites (IAM/S3/quotas), instance sizing, SageMaker AI vs HyperPod. Produces runnable starter code.              |
| **sagemaker-python-sdk-v3**   | Deep SDK reference      | Writing/debugging non-trivial SDK V3 code: `ModelTrainer`, `ModelBuilder`, Pipelines (`sagemaker-mlops`), resources/endpoints, experiments, lineage, JumpStart, fine-tuning (SFT/DPO/RLVR/RLAIF), V2→V3 migration. |
| **sagemaker-hyperpod-cli**    | Deep HyperPod reference | The `hyp` CLI + `sagemaker-hyperpod` SDK (EKS-orchestrated): training jobs, inference endpoints, cluster stacks, dev spaces, CRDs, templates, quota allocation.                                                    |

Start with **getting-started**; it hands off to the two deep references when you
need exact APIs or HyperPod internals. Install all three for the full experience.

## Repository layout

```
claude-code/skills/<name>/SKILL.md + topic .md (+ templates/)   # Claude Code
amazon-quick/skills/<name>/SKILL.md + topic .md (+ templates/)  # Amazon Quick
kiro/powers/<name>/POWER.md + steering/*.md                     # Kiro
```

Each agent folder has its own README with exact install steps:

- [`claude-code/README.md`](claude-code/README.md)
- [`amazon-quick/README.md`](amazon-quick/README.md)
- [`kiro/README.md`](kiro/README.md)

## Quick install per agent

**Claude Code** — copy (or symlink) the skills into your skills dir:

```bash
cp -R claude-code/skills/* ~/.claude/skills/
```

**Amazon Quick** — copy each skill into your Quick profile's skills path:

```bash
cp -R amazon-quick/skills/* ~/.quickwork/profiles/<your-profile>/skills/
```

**Kiro** — in the command palette run **Kiro: Add Power** and paste this repo's
URL (Kiro clones the powers under `.kiro/powers/`). Or copy a power folder into
`<workspace>/.kiro/powers/`.

Start a new session/conversation after installing — manifests load at startup.

## Requirements

- Generates **SageMaker Python SDK V3** code; install what a task needs:
  `pip install sagemaker-core sagemaker-train sagemaker-serve sagemaker-mlops`
- SDK V3 targets **Python ≤ 3.13** (not yet compatible with 3.14+).
- HyperPod CLI work uses `pip install sagemaker-hyperpod` (the `hyp` command).
- An AWS account with appropriate IAM permissions, an S3 bucket, and service
  quotas for the instance types you use (getting-started walks through these).

## Scope & honesty notes

- These are **guidance and reference**, not a substitute for the official
  [AWS documentation](https://docs.aws.amazon.com/sagemaker/). API details, GPU
  specs, CUDA compatibility, and HyperPod CLI commands evolve across versions —
  the content tells the agent to verify version-sensitive specifics rather than
  asserting them.
- Code patterns are derived from the SDK V3 API surface; always validate against
  your installed package versions and a real run.
- The Amazon Quick and Kiro manifest formats follow conventions from public
  community examples; verify against current Amazon Quick / Kiro documentation,
  as those formats may evolve.
