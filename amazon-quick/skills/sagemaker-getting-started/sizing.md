# Instance Sizing & Cost (self-contained)

Pick an instance that fits the model, then sanity-check time and cost. These are
planning estimates — always validate with a real run. For exact, current specs
and prices, see the public AWS links at the bottom.

## Quick rule of thumb (LLM memory)

Training memory per GPU is dominated by: \*\*weights + optimizer states + gradients

- activations\*\*. A practical shortcut in bytes:

| Mode                                       | Rough VRAM needed (full model)                                        |
| ------------------------------------------ | --------------------------------------------------------------------- |
| **Full fine-tune, mixed precision (Adam)** | ~ **16 × params(B)** GB (2 weights + 4 master + 8 optimizer + 2 grad) |
| **LoRA (frozen base, fp16)**               | ~ **2 × params(B)** GB + small adapter/optimizer                      |
| **QLoRA (4-bit base)**                     | ~ **0.5 × params(B)** GB + small adapter/optimizer                    |
| **Inference (fp16)**                       | ~ **2 × params(B)** GB + KV-cache (grows with batch × context)        |

Add ~20-40% headroom for activations, CUDA/framework overhead, and fragmentation.
If the number exceeds one GPU's memory, you need **multiple GPUs + sharding**
(ZeRO/FSDP) or tensor/pipeline parallelism.

Examples:

- Llama 3 8B, QLoRA → ~4 GB + overhead → fits **one 24 GB GPU** (g5.2xlarge).
- Llama 3 8B, full FT → ~128 GB → needs **multiple GPUs** (e.g. 8×A10G or a p4d) + FSDP/ZeRO.
- Llama 3 70B, LoRA → ~140 GB → **8-GPU** node (g5.48xlarge or p4d) with sharding.
- Llama 3 70B, inference fp16 → ~140 GB + KV → **8×A10G/p4d** or 2×H100.

## GPU instance cheat-sheet (capacity, not price)

| Instance                   | GPUs × mem           | Good for                                         |
| -------------------------- | -------------------- | ------------------------------------------------ |
| `ml.g5.xlarge` / `2xlarge` | 1 × A10G 24 GB       | QLoRA/LoRA small models (≤8B), small inference   |
| `ml.g5.12xlarge`           | 4 × A10G 24 GB (96)  | LoRA mid models, multi-GPU practice              |
| `ml.g5.48xlarge`           | 8 × A10G 24 GB (192) | LoRA 70B, full FT of small models, LLM inference |
| `ml.g6 / g6e`              | 1-8 × L4 / L40S      | newer cost-efficient alternative to g5           |
| `ml.p4d.24xlarge`          | 8 × A100 40 GB (320) | full FT mid models, 70B work                     |
| `ml.p4de.24xlarge`         | 8 × A100 80 GB (640) | larger full FT, big inference                    |
| `ml.p5.48xlarge`           | 8 × H100 80 GB (640) | large-scale training, fastest                    |
| `ml.m5 / c5 (CPU)`         | no GPU               | classic ML (sklearn/XGBoost), small jobs         |

Use the smallest thing that fits — bigger instances cost more per second. Start
small (even a subset of data) to validate the pipeline, then scale.

## Sharding / parallelism (when one GPU isn't enough)

| Strategy               | Shards                   | Use when                             |
| ---------------------- | ------------------------ | ------------------------------------ |
| ZeRO-1                 | optimizer states         | mild pressure, multi-GPU             |
| ZeRO-2                 | + gradients              | more pressure                        |
| ZeRO-3 / FSDP          | + model weights          | model itself won't fit one GPU       |
| Tensor parallel (TP)   | layers across GPUs       | very large layers / single big model |
| Pipeline parallel (PP) | layer groups across GPUs | very deep models, many nodes         |

For getting started: prefer **FSDP** (PyTorch-native) or **ZeRO** before reaching
for TP/PP. Total GPUs needed ≈ (full memory ÷ per-GPU memory), rounded up to a
node size, then verified empirically.

## Rough training-time intuition

`time ≈ (6 × active_params × total_tokens) / (num_gpus × per_GPU_FLOPS × MFU)`

- `6 × params × tokens` is the standard training-FLOPs estimate.
- `MFU` (model FLOPs utilization) is typically **0.3-0.5** in practice.
- Use published per-GPU BF16 TFLOPS (e.g. A100 ~312, H100 ~989) for `per_GPU_FLOPS`.

This is a floor — real time is longer due to data loading, checkpointing, eval,
and communication. For fine-tuning (few epochs on a small dataset) it's usually
minutes-to-hours, not days.

## Cost estimation

Cost ≈ `instance_hourly_price × num_instances × hours`. Get current per-region
hourly prices from the SageMaker pricing page (link below). Reminder to state:
**endpoints bill continuously until deleted**, and **HyperPod clusters bill while
running** — training jobs only bill while the job runs.

## Public AWS references (safe to share with anyone)

- SageMaker pricing: https://aws.amazon.com/sagemaker/pricing/
- ML instance types: https://aws.amazon.com/sagemaker/pricing/instance-types/
- Service Quotas console: https://console.aws.amazon.com/servicequotas/
- Distributed training (SDK): https://docs.aws.amazon.com/sagemaker/latest/dg/distributed-training.html
