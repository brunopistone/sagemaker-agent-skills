# SageMaker Powers for Kiro

Three [Kiro Powers](https://kiro.dev/docs/powers/). Each is a folder with a
`POWER.md` manifest (Kiro frontmatter: `name`, `displayName`, `description`,
`keywords`, `author`) plus a `steering/` directory of context files that Kiro
auto-loads when relevant.

```
kiro/powers/
├── sagemaker-getting-started/   POWER.md + steering/*.md (+ steering/templates/)
├── sagemaker-python-sdk-v3/     POWER.md + steering/*.md
└── sagemaker-hyperpod-cli/      POWER.md + steering/*.md
```

Each `POWER.md` ends with a **"When to load steering files"** map so Kiro pulls
only the relevant file for a given request.

## Install

### Option A — Kiro: Add Power (clone from Git)

1. Open the command palette (`Cmd+Shift+P` / `Ctrl+Shift+P`) and run
   **Kiro: Add Power**.
2. Paste this repository's Git URL. Kiro clones the powers under
   `.kiro/powers/`.
3. Confirm the powers appear in the Kiro Powers panel.

(If Kiro expects a power at the repo root, point it at a specific power's path,
or use Option B.)

### Option B — copy into the workspace

```bash
mkdir -p /path/to/your-project/.kiro/powers
cp -R kiro/powers/* /path/to/your-project/.kiro/powers/
```

After install, confirm the structure, e.g.:

```
.kiro/powers/sagemaker-getting-started/
  POWER.md
  steering/
    guardrails.md
    decision-guide.md
    ...
```

Then ask, e.g. _"I'm new to SageMaker — help me fine-tune Llama 3 8B and tell me
which instance to use."_

## Requirements

- Kiro IDE.
- For the code these powers generate: Python ≤ 3.13 and the SDK V3 packages
  (`pip install sagemaker-core sagemaker-train sagemaker-serve sagemaker-mlops`);
  HyperPod work uses `pip install sagemaker-hyperpod`.

> Note: the `POWER.md` format here follows conventions from public community
> examples and the Kiro Powers docs. Kiro also natively supports `.kiro/steering/`
> files and `AGENTS.md`; verify against current Kiro documentation, as formats may
> evolve.
