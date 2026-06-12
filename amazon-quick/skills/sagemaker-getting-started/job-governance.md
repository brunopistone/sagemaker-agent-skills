# Job governance: queue & prioritize training jobs (AWS Batch)

Goal: when **multiple users/teams share a capacity budget**, stop training jobs
from failing on "no capacity" and instead **queue, prioritize, and fair-share**
them. SageMaker Training jobs integrate with **AWS Batch**: you submit the same
`ModelTrainer` job to a Batch **job queue**, and Batch dispatches it to a
**service environment** when capacity is free. Your training code does not change
— the PySDK passes the payload straight to `CreateTrainingJob`.

Use this for **multi-tenant governance** (e.g. Team A vs Team B sharing GPUs),
not for one-off solo jobs. Needs `sagemaker>=3.7` and AWS Batch permissions.

## The four AWS Batch resources

| Resource | What it does | Key fields |
|---|---|---|
| **Service environment** | Caps max concurrent training **instances** per team (capacity budget) | `serviceEnvironmentType=SAGEMAKER_TRAINING`, `capacityLimits` (`capacityUnit=NUM_INSTANCES`, `maxCapacity`) |
| **Job queue** | Holds/schedules jobs; one per team | `jobQueueType=SAGEMAKER_TRAINING`, `priority` (1–9999, higher served first when sharing a service env), `serviceEnvironmentOrder` |
| **Scheduling policy** | Fair-share ordering (FIFO queues skip this) | share identifiers + `weightFactor`, `shareDecaySeconds` |
| **Quota share** | Capacity allocation for quota-management queues | `sharingStrategy` (`LEND_AND_BORROW`/`LEND`/`RESERVE`), `borrowLimit`, `inSharePreemption` |

A service-linked role **`AWSServiceRoleForAWSBatchWithSagemaker`** is created
automatically the first time you create a SageMaker service environment.

## Three queue types

- **FIFO** — jobs run in submission order. Simplest; no scheduling policy.
- **Fair-share** — jobs ordered by **share identifier** weights + recent usage
  history. `weightFactor`: **lower weight = more resources** (weight=1 gets ~5×
  the share of weight=5). `shareDecaySeconds` (min 600; 0 → defaults to 600)
  controls how long past usage influences scheduling.
- **Quota-management** — capacity split into quota shares with **lending,
  borrowing, and preemption**.

## Submit a job to a queue (PySDK)

Build the `ModelTrainer` exactly as in `llm-finetuning.md` (Option 2), then submit
it to the queue instead of calling `.train()`:

```python
from sagemaker.train.aws_batch.training_queue import TrainingQueue

# 1. Build model_trainer = ModelTrainer(...) and the input `data` list as usual.

# 2. Point at your team's queue.
SMTJ_BATCH_QUEUE = "team-b-queue"
queue = TrainingQueue(SMTJ_BATCH_QUEUE)

# 3. Submit. For a fair-share queue, share_identifier + priority are required.
queued_job = queue.submit(
    model_trainer,                 # the ModelTrainer
    data,                          # list[InputData] channels
    job_name,
    share_identifier="HIGHPRI",    # a named priority tier (fair-share queues)
    priority=1,
)
```

Inspect and manage queued jobs:

```python
queue.list_jobs(status="RUNNABLE")          # SUBMITTED/RUNNABLE/STARTING/RUNNING/SUCCEEDED/FAILED
queued_job.describe()                        # status, jobName, ...
queued_job.terminate()                       # cancel an in-queue job
# job.update(scheduling_priority=N)          # change priority after submission
```

For Quota-management queues, submit with a `quota_share_name` instead of a
share identifier. The Batch scheduler then picks the next job by: queue priority
(across queues sharing a service env) → share-identifier weights (within a
fair-share queue) → job priority → FIFO.

## IAM (multi-tenant setup)

- One **IAM role per team**; users assume it via `sts:AssumeRole`.
- Scope **`batch:SubmitServiceJob`** to that team's queue ARN, e.g.
  `arn:aws:batch:<region>:<account>:job-queue/team-a-queue`.
- The SageMaker execution role needs **`iam:PassRole`** with condition
  `iam:PassedToService: sagemaker.amazonaws.com`.
- The notebook/role submitting jobs needs AWS Batch API permissions.

## When to use it

- **Use** when teams share a fixed instance budget and you need priority/fairness,
  or want jobs to **wait in a queue rather than fail** when capacity is full.
- **Skip** for a single user running occasional jobs — plain `ModelTrainer.train()`
  (see `llm-finetuning.md`) is simpler.
- This is **not** HyperPod (a persistent cluster); it governs ordinary managed
  training jobs. See `decision-guide.md`.

## Cost & cleanup

Service environments cap concurrent instances (cost guardrail). Queued jobs don't
bill until they run. Tear down resources in order — **quota shares → job queues →
service environments → scheduling policies** — each disabled before delete.

> The `aws_batch` PySDK helpers (`TrainingQueue`, `TrainingQueuedJob`) and Batch
> API field names evolve — verify against current AWS docs
> (docs.aws.amazon.com/batch/latest/userguide/getting-started-sagemaker.html) and
> your installed `sagemaker` version.
