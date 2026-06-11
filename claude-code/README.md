# SageMaker Skills for Claude Code

Three [Claude Code](https://code.claude.com) Agent Skills. Each is a folder with a
`SKILL.md` plus topic files (and, for getting-started, runnable `templates/`).

```
claude-code/skills/
├── sagemaker-getting-started/   SKILL.md + topic .md + templates/
├── sagemaker-python-sdk-v3/     SKILL.md + topic .md
└── sagemaker-hyperpod-cli/      SKILL.md + topic .md
```

## Install

Claude Code discovers skills in `~/.claude/skills/` (personal) or
`<repo>/.claude/skills/` (project-scoped).

### Personal (all your projects)

```bash
git clone <this-repo-url> sagemaker-agent-skills
cd sagemaker-agent-skills

mkdir -p ~/.claude/skills
# copy:
cp -R claude-code/skills/* ~/.claude/skills/
# or symlink each (edits in the repo stay live):
ln -s "$PWD/claude-code/skills/sagemaker-getting-started" ~/.claude/skills/sagemaker-getting-started
ln -s "$PWD/claude-code/skills/sagemaker-python-sdk-v3"  ~/.claude/skills/sagemaker-python-sdk-v3
ln -s "$PWD/claude-code/skills/sagemaker-hyperpod-cli"   ~/.claude/skills/sagemaker-hyperpod-cli
```

### Project (one repo / team)

```bash
mkdir -p /path/to/your-project/.claude/skills
cp -R claude-code/skills/* /path/to/your-project/.claude/skills/
```

Start a **new** Claude Code session after installing (skills load at startup),
then try: _"I'm new to SageMaker and want to fine-tune Llama 3 8B on my data."_
