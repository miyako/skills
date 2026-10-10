#!/usr/bin/env bash
# Build the content of the `dist` branch from a commit of main.
#
#   .github/scripts/build_dist.sh <out-dir> [<commit>]
#
# <out-dir> receives (at its root): the content of 4d-skills/ that consumers
# need (AGENTS.md, MIGRATION.json, skills/, schemas/), plus README.md (links
# rewritten for the new root) and VERSION. Nothing from vendor/, Project/ or
# .github/. Existing content of <out-dir> other than .git is removed.
set -euo pipefail

out=${1:?usage: build_dist.sh <out-dir> [<commit>]}
rev=${2:-HEAD}
include=(4d-skills/AGENTS.md 4d-skills/MIGRATION.json 4d-skills/skills 4d-skills/schemas)

mkdir -p "$out"
find "$out" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +

git archive --format=tar "$rev" "${include[@]}" | tar -x -C "$out" --strip-components=1
git show "$rev:VERSION" > "$out/VERSION"
# README.md links point into 4d-skills/ on main; on dist that folder is the root.
git show "$rev:README.md" \
  | sed -e 's#](4d-skills/#](#g' -e 's#](4d-skills)#](.)#g' \
  > "$out/README.md"
