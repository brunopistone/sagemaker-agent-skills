# Decision Guide: where should this run?

Use this to make the choices below for the user, in plain language.

## Choice 0 (fine-tuning/customizing an LLM): how much infra to manage

| Option | You manage | Pick when |
| ------ | ---------- | --------- |
| **Serverless model customization** (`serverless-customization.md`) | nothing — base model + dataset + technique | the base model & technique are supported; you want the easiest path, no instance/quota |
| **Managed job, your script** (`llm-finetuning.md` Option A) | instance type + a `train.py` | custom training logic or an unsupported model |
| **Managed job from a recipe** (`llm-finetuning.md` Option B) | instance type | a curated recipe fits your model/technique |
| **HyperPod recipe job** (`hyperpod.md`) | a persistent cluster | big/long runs; the same recipe on a resilient cluster |
| **HyperPod custom PyTorch job** (`hyperpod-cli-reference.md`) | cluster + your container/script | custom code at scale on a resilient cluster |

The first three are **managed (no cluster)**; the last two run on a **HyperPod
cluster** you provision and keep running. Default to **serverless customization**
for newcomers fine-tuning a supported model — no hardware to size, no quota to
request. Move down the list only when you need more control or scale; reach for
HyperPod only when a managed job isn't enough.

## Choice 1: SageMaker AI vs HyperPod

**Default to SageMaker AI managed jobs/endpoints.** It's the easy on-ramp: no
cluster to provision, compute spins up per job and tears down automatically, you
pay only while it runs.

| Pick **SageMaker AI** (managed) when...    | Pick **HyperPod** when...                                            |
| ------------------------------------------ | -------------------------------------------------------------------- |
| One-off or occasional training/fine-tuning | Long-running, multi-day/multi-week training                          |
| You don't want to manage infrastructure    | You want a persistent cluster to reuse across many jobs              |
| Small-to-medium models, single job         | Very large-scale distributed training (many nodes)                   |
| Deploying a model behind an endpoint       | You need resiliency: auto-detect & replace failed nodes, auto-resume |
| "I just want to get something working"     | You need direct node access / HPC-style workflow                     |

One-line rule to tell the user: _"Managed jobs are rented-by-the-job and zero-ops;
HyperPod is a cluster you own and keep running for big, long, or failure-prone
training."_

Note: both can run the **same recipes**. `ModelTrainer.from_recipe(...)` in the
SDK V3 launches a recipe as a managed job; the same recipe family also runs on
HyperPod. So a user can start managed and graduate to HyperPod later without
rewriting the training logic.

## Choice 2 (HyperPod only): Slurm vs EKS orchestrator

A HyperPod cluster is one orchestrator or the other, chosen at creation.

|                               | **Slurm**                                               | **Amazon EKS**                                             |
| ----------------------------- | ------------------------------------------------------- | ---------------------------------------------------------- |
| Feels like                    | Traditional HPC (`sbatch`, `squeue`, `srun`)            | Kubernetes (`kubectl`, pods)                               |
| VPC                           | Optional (platform-managed by default)                  | Mandatory                                                  |
| Lowest-friction first cluster | ✅ Console "Quick setup" auto-creates VPC, S3, IAM, FSx | Requires an EKS cluster + VPC                              |
| Newest tooling target         | —                                                       | ✅ The `hyp` CLI, SDK, inference, and Spaces are EKS-first |

Guidance for a newcomer:

- **Just want the simplest first cluster, HPC-style** → **Slurm Quick setup** in the console.
- **Plan to grow into containerized training + inference, or want the new `hyp` CLI/SDK** → **EKS**.

Both are first-class in AWS docs; "recommended" depends on where the user is
heading. State the trade-off and let them choose.

## When to just NOT use SageMaker yet

If the user only wants to _try_ a model interactively (no training, tiny scale),
it's honest to say a local run or a JumpStart one-click deploy may be enough, and
SageMaker training jobs are overkill. Don't push infrastructure they don't need.
