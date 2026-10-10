---
name: technote-release
description: >
  Publish the localised PDF and the zipped 4D demo as a GitHub release.
  Use when the user asks to release, tag, or publish the localised
  technical note. Only applies in a 4D technote-localisation repository
  (one with technote.json at the root, created from
  miyako/4d-technote-localisation-template); do not use elsewhere.
---

# Release the localised technical note

> **Scope:** technote-localisation repositories only -- the repository root
> has a `technote.json`. The `make` targets, `src/`, `figures/`, `demo/` and
> `tools/` paths below belong to that template. In any other repository,
> do not use this skill.

1. **Preconditions:**
   - `make check` passes and `make` builds.
   - `git status` is clean (`make demo-zip` archives **committed** files only: `git archive HEAD:demo/<Name>`).
   - Uncommitted changes: list them and ask whether to commit them or leave them out. Deletions count too.
2. **README:** if `README.md` is still the template's usage guide, replace it with
   `.github/templates/README.technote.md`. Fill in every `{{PLACEHOLDER}}` from real data and delete the template
   comments. `{{RELEASE_URL}}` is `https://github.com/<owner>/<repo>/releases/tag/<tag>`, or use
   `releases/latest/download/<file>` links. Commit it with the release preparation.
3. **Merge first** if the work is on a branch: push it, open a PR (use the PR tool if available, otherwise
   `gh pr create`), and merge it once the user agrees. Releases are tagged on the default branch.
4. **Confirm with the user (checkpoint):**
   - the README
   - the tag (e.g. `v1.0.0`)
   - the release title (e.g. the translated document title)
   - the notes: a short description in the target language and/or English, plus what is included
   - the assets: `build/<stem>_<tgt>.pdf` and `build/<Name>.zip` for each project in `demo/`
5. **Build from a tree identical to the default branch.** Check out or pull it, then:
   ```sh
   make clean && make release-assets
   ```
   Check the PDF's page count and the zip's contents (`unzip -l`): no `Data/`, `DerivedData/` or
   `userPreferences.*`.
6. **Publish:**
   ```sh
   git tag vX.Y.Z <default-branch-sha> && git push origin vX.Y.Z
   gh release create vX.Y.Z build/*_<tgt>.pdf build/*.zip --title "…" --notes-file notes.md
   ```
   In the cloud agent, without permission to create releases: push the tag only if allowed, otherwise ask the user
   to push it. `.github/workflows/release.yml` then builds the assets on Linux and attaches them. Tell the user that
   the Linux fonts differ from a macOS build.
7. Report the release URL and the asset sizes. Delete temporary files (e.g. `notes.md`).
