#!/usr/bin/env python3
"""
Deploy and invoke an LLM endpoint on SageMaker AI (SDK V3, ModelBuilder).

Prerequisites:
  pip install sagemaker-serve
  - An execution role; endpoint-usage quota for the instance
  - For gated models: accept the HF license and set HF_TOKEN

WARNING: a real-time endpoint bills continuously until deleted. This script
deletes it at the end unless KEEP_ENDPOINT = True.

Edit CONFIG, then: python deploy_llm_endpoint.py
"""

from sagemaker.serve import ModelBuilder
from sagemaker.serve.builder.schema_builder import SchemaBuilder

# ----------------------- CONFIG (edit me) -----------------------
MODEL = "meta-llama/Llama-3.1-8B-Instruct"   # HF ID, JumpStart ID, or an S3 artifact
ENDPOINT_NAME = "my-llm-endpoint"
INSTANCE_TYPE = "ml.g5.2xlarge"
INSTANCE_COUNT = 1
HF_TOKEN = None                              # set for gated models
PROMPT = "Write a haiku about the sea."
KEEP_ENDPOINT = False                        # True to leave it running (keeps billing!)
# ----------------------------------------------------------------


def main():
    model_env = {"HF_TOKEN": HF_TOKEN} if HF_TOKEN else None

    builder = ModelBuilder(
        model=MODEL,
        env_vars=model_env,
        schema_builder=SchemaBuilder(
            sample_input={"inputs": "Hello, who are you?"},
            sample_output={"generated_text": "I am an assistant."},
        ),
    )

    builder.build()
    endpoint = builder.deploy(
        endpoint_name=ENDPOINT_NAME,
        instance_type=INSTANCE_TYPE,
        initial_instance_count=INSTANCE_COUNT,
    )
    print(f"Endpoint '{ENDPOINT_NAME}' is live.")

    import json
    resp = endpoint.invoke(
        body=json.dumps({"inputs": PROMPT}).encode(),
        content_type="application/json",
        accept="application/json",
    )
    print("Response:", resp)

    if not KEEP_ENDPOINT:
        print("Cleaning up endpoint to stop billing...")
        endpoint.delete()
        endpoint.wait_for_delete()
        print("Deleted.")
    else:
        print("KEEP_ENDPOINT=True — remember to delete it later to stop billing.")


if __name__ == "__main__":
    main()
