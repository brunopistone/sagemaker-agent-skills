# V2 -> V3 Migration

The repo's full migration guide lives at `migration.md` (repo root). This is the quick mapping.

## V2 -> V3 Key Mapping

| V2 | V3 | Package |
|----|-----|---------|
| `Estimator` | `ModelTrainer` | sagemaker-train |
| `PyTorch/TensorFlow/SKLearn` estimators | `ModelTrainer` + `image_uris.retrieve()` | sagemaker-train |
| `.fit()` | `.train()` | sagemaker-train |
| `TrainingInput` | `InputData` | sagemaker-train |
| `Model` | `ModelBuilder` | sagemaker-serve |
| `Predictor` | `Endpoint.invoke()` | sagemaker-core |
| `model.deploy()` | `ModelBuilder.build()` + `.deploy()` | sagemaker-serve |
| `sagemaker.workflow.pipeline.Pipeline` | `sagemaker.mlops.workflow.Pipeline` | sagemaker-mlops |
| `instance_type="local"` | `training_mode=Mode.LOCAL_CONTAINER` | sagemaker-train |
| `distribution={"smdistributed": ...}` | `distributed=Torchrun(smp=SMP(...))` | sagemaker-train |

## V3-Only Features (no V2 equivalent)
- **SFTTrainer/DPOTrainer/RLVRTrainer/RLAIFTrainer** - Foundation model fine-tuning
- **BenchMarkEvaluator/LLMAsJudgeEvaluator** - Model evaluation framework
- **AI Registry Hub** - Dataset/evaluator management
- **BedrockModelBuilder** - Deploy to Bedrock
- **In-Process Mode** - No-container local inference
- **Nova recipe training** - Nova model fine-tuning
- **EMRServerlessStep** - EMR Serverless in pipelines
- **Resource chaining** - `ModelBuilder(model=model_trainer)`
