# SageMaker Skills for Amazon Quick

Three Amazon Quick skills. Each is a folder with a `SKILL.md` (Quick frontmatter:
`name`, `display_name`, `description`, `icon`, `trigger`) plus topic files.

```
amazon-quick/skills/
├── sagemaker-getting-started/   SKILL.md + topic .md + templates/
├── sagemaker-python-sdk-v3/     SKILL.md + topic .md
└── sagemaker-hyperpod-cli/      SKILL.md + topic .md
```

These skills are **documentation/reference** skills (pure markdown — no bundled
Python engine to auto-import), so they have no external dependencies and no
hardcoded paths.

## Install

Copy each skill folder into your Amazon Quick profile's skills path, then restart
Quick (or start a new conversation):

```bash
# replace <your-profile> with your Quick profile name (e.g. federate-prod)
cp -R amazon-quick/skills/sagemaker-getting-started ~/.quickwork/profiles/<your-profile>/skills/sagemaker-getting-started
cp -R amazon-quick/skills/sagemaker-python-sdk-v3  ~/.quickwork/profiles/<your-profile>/skills/sagemaker-python-sdk-v3
cp -R amazon-quick/skills/sagemaker-hyperpod-cli   ~/.quickwork/profiles/<your-profile>/skills/sagemaker-hyperpod-cli
```

The skill activates automatically when you ask about getting started with
SageMaker, training, deploying, or sizing — e.g. _"How do I fine-tune Llama 3 8B
on SageMaker, and what instance do I need?"_

## Requirements

- Amazon Quick desktop app.
- For the code these skills generate: Python ≤ 3.13 and the SDK V3 packages
  (`pip install sagemaker-core sagemaker-train sagemaker-serve sagemaker-mlops`).

> Note: the Quick `SKILL.md` frontmatter here follows conventions from public
> community examples. Verify against current Amazon Quick documentation, as the
> format may evolve.
