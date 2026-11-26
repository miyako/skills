# Workflows for a Demo Repository

Both files go in `.github/workflows/`. They assume `.gitmodules` declares
`.agents` on branch `dist` of `https://github.com/miyako/skills.git`.

## `update-skills.yml`

Weekly bump of the `.agents` pointer. `actions/checkout` fetches only the
pinned submodule commit, so fetch the branch tip explicitly.

```yaml
# Moves the `.agents` submodule (miyako/skills, branch dist) to the latest commit and pushes the new
# pointer to the default branch. Runs weekly and on demand. Nothing is committed when skills are unchanged.
name: Update skills

on:
  schedule:
    - cron: "17 3 * * 1"   # Mondays 03:17 UTC
  workflow_dispatch:

permissions:
  contents: write

concurrency:
  group: update-skills
  cancel-in-progress: false

jobs:
  update-skills:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.repository.default_branch }}
          submodules: true

      # actions/checkout fetches only the pinned commit of the submodule (shallow, no branch refs),
      # so fetch the tip of the branch named in .gitmodules explicitly before moving to it.
      - name: Update .agents to the tip of its branch
        run: |
          branch="$(git config -f .gitmodules submodule..agents.branch || echo dist)"
          git submodule update --init .agents
          git -C .agents fetch --depth=1 origin "+refs/heads/${branch}:refs/remotes/origin/${branch}"
          git -C .agents checkout -q --detach "origin/${branch}"

      - name: Commit and push if the pointer changed
        run: |
          if git diff --quiet -- .agents; then
            echo "Skills are up to date."
            exit 0
          fi
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add .agents
          git commit -m "Update skills (.agents → miyako/skills@$(git -C .agents rev-parse --short HEAD))"
          git push origin "HEAD:${{ github.event.repository.default_branch }}"
```

## `copilot-setup-steps.yml`

The job name `copilot-setup-steps` is required; keep `submodules: true`.

```yaml
# Prepares the environment for the GitHub Copilot cloud agent.
# https://docs.github.com/copilot/customizing-copilot/customizing-the-development-environment-for-copilot-coding-agent
# The job name `copilot-setup-steps` is required. Keep `submodules: true` on the checkout step so the
# agent sees the skills in `.agents/` (miyako/skills, branch dist). Add repository-specific steps below it.
name: Copilot setup steps

on:
  workflow_dispatch:
  push:
    paths: [.github/workflows/copilot-setup-steps.yml]
  pull_request:
    paths: [.github/workflows/copilot-setup-steps.yml]

jobs:
  copilot-setup-steps:   # this job name is required
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: true

      - name: Check skills
        run: test -f .agents/AGENTS.md && ls .agents/skills
```
