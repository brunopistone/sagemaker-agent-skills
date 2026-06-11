# AutoML with AutoGluon (let the toolkit pick the model)

Goal: get a strong model **without** choosing the algorithm or tuning by hand —
ideal for newcomers with tabular data who just want good predictions. AutoGluon
trains and ensembles many models automatically. This is often the fastest path
from "I have a CSV" to "I have a working model."

## When to suggest this

- The user has **tabular data** (a CSV/parquet with a target column) and isn't
  attached to a specific algorithm → AutoGluon is usually the best starting point.
- They say "I don't know which model to use" / "just make it accurate."
- Also supports **time-series forecasting** and **multimodal** (text+image+tabular),
  but tabular is the common on-ramp.

If they specifically want one framework (sklearn/XGBoost) or an LLM, route to
`classic-ml-training.md` or `llm-finetuning.md` instead.

## Two ways to run it

### A) Simplest: AutoGluon locally / in a notebook, then deploy

For small-to-medium tabular data, AutoGluon runs fine in a notebook or on a single
instance:

```python
# pip install autogluon
from autogluon.tabular import TabularPredictor
import pandas as pd

train = pd.read_csv("train.csv")
predictor = TabularPredictor(label="target").fit(train)   # tries many models + ensembles
predictor.leaderboard()                                    # see what won
preds = predictor.predict(pd.read_csv("test.csv"))
predictor.save("ag_model")
```

Then package/deploy the saved predictor as a SageMaker endpoint via `ModelBuilder`
(see `classic-ml-inference.md`) using an AutoGluon/PyTorch container.

### B) As a SageMaker training job (scale / managed)

Wrap an AutoGluon training script in `ModelTrainer` (same contract as
`classic-ml-training.md`): the script calls `TabularPredictor(...).fit(...)` on the
data mounted at `/opt/ml/input/data/<channel>/` and saves the predictor to
`/opt/ml/model/`. Use this when the data is large or you want a reproducible
managed job. Resolve the container with `image_uris.retrieve(framework="autogluon", ...)`.

## Sizing

AutoGluon tabular is usually CPU-bound — start on an `ml.m5`/`ml.c5` instance.
It trains _many_ models, so give it enough CPU/RAM and a sensible `time_limit` in
`.fit(time_limit=...)` to cap runtime/cost. Multimodal/large data may justify a GPU.

## Verify, cost, cleanup

- Check `predictor.leaderboard()` to see which models were tried and the validation
  scores — a good plain-language "did it work?" signal.
- Managed jobs stop billing on completion; a deployed endpoint bills until deleted
  (same cleanup as `classic-ml-inference.md`).

## Public references

- AutoGluon: https://auto.gluon.ai/
- SageMaker built-in / framework containers: https://docs.aws.amazon.com/sagemaker/latest/dg/algorithms-choose.html
