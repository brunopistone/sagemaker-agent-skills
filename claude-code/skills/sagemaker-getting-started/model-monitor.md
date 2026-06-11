# Monitoring a deployed model (Model Monitor)

Goal: once a model is behind an endpoint, watch it for problems over time. This
is a "day 2" concern — only relevant after `llm-inference.md` /
`classic-ml-inference.md`. Code uses SDK V3.

## Plain-language: what each monitor watches

| Monitor type                  | Catches                                                                                             | Ask if the user cares about...                               |
| ----------------------------- | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| **Data quality**              | Incoming requests drifting from the training data (new ranges, missing/extra columns, type changes) | "are the inputs in production still like what I trained on?" |
| **Model quality**             | Predictions degrading vs. actual outcomes (accuracy/precision over time)                            | "is my model still accurate?" (needs ground-truth labels)    |
| **Bias drift**                | Fairness metrics shifting across groups after deployment                                            | regulated / fairness-sensitive use cases                     |
| **Feature attribution drift** | The _importance_ of features changing (explainability drift)                                        | "are different features driving predictions now?"            |

Start newcomers with **data quality** — it needs no labels and catches the most
common real-world failure (the world changed, the model didn't).

## Prerequisite: capture endpoint traffic

Monitoring works off **data capture** — the endpoint must log a sample of
requests/responses to S3. Enable this at deploy time (a data-capture config on the
endpoint) or update the endpoint to add it. Without capture, there's nothing to
monitor. Confirm this is on before setting up any schedule.

## The flow (all four monitor types share it)

1. **Baseline** — run a baselining job over the training (or a reference) dataset
   to learn the expected statistics/constraints; it writes `statistics.json` and
   `constraints.json` to S3.
2. **Schedule** — create a monitoring schedule (e.g. hourly/daily) that compares
   captured traffic against the baseline.
3. **Review** — each run emits a violations report to S3 and metrics to CloudWatch;
   wire a CloudWatch alarm to get notified.

Model Monitor lives in `sagemaker-core` (`model_monitor/` — monitoring configs and
alert definitions). Use `get_execution_role()` / `Session()` as elsewhere, and an
`ml.m5`-class instance for the monitoring jobs (CPU is fine).

## Known footguns (warn the user)

- **No capture = no monitoring.** The #1 mistake is creating a schedule on an
  endpoint that never had data capture enabled.
- **Model quality needs ground truth.** You must deliver actual outcomes (labels)
  to S3 for the job to compare against — it can't measure accuracy without them.
- **Baseline must match the schema.** If the baseline dataset columns/types don't
  match what the endpoint receives, every run reports violations.
- API surface here has historically had rough edges across SDK versions — if a
  specific monitor constructor/arg is rejected, verify against the current
  SageMaker docs rather than forcing it.

## Cost & cleanup

Monitoring jobs bill per run and data capture stores objects in S3. Delete the
monitoring **schedule** when you stop needing it (otherwise it keeps launching
jobs), and clean up captured data if it grows large.

## Public reference

- Model Monitor docs: https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor.html
