---
name: demo-shareable-repo
description: >
  Turn a 4D demo project into a repository that attendees can clone and run
  on their own machine: survey for hidden config and leftovers, the .agents
  skills submodule with its weekly update workflow, opening straight into
  the demo form, first-launch downloads with in-form status, UI language
  following the OS, version pinning, and the bilingual developer-facing
  README. Use when preparing, polishing or publishing a demo, webinar or
  seminar project that will be shared.
---

# Attendee-Shareable Demo Repository

Attendees clone the repository, open it in 4D and expect it to work with
no explanation. Everything they need is either in Git, downloaded
automatically, or one documented download from Releases.

## Related

| Topic | Skill |
|---|---|
| Inherited-project survey (compatibilityVersion, hidden config, scratch methods, trash) | `4dproject` ("Surveying an Inherited Project") |
| Large data files: Git, LFS or release ZIP | `demo-data-distribution` |
| Local embedding models | `4dembeddings` |
| Vector-search demo specifics | `demo-vector-search` |
| Live presentation, Japanese audience | `demo-presentation` |
| Localisation | `4dlocalise` |
| Visual polish | `polish-ui-pass` |

## Workflow

One branch per effort. Stop after the survey and after each effort for the
owner's review. Earlier template instructions (e.g. HDI_Template) are a
baseline only: confirm current choices with the owner.

1. **Survey** (`4dproject`) and record findings before changing anything.
2. **Version.** `compatibilityVersion` in the `.4DProject` matches the 4D
   release named in the repository and README badge (a "21R5" repo had
   21 R6 = 2160). Set it to the lowest release the demo supports.
3. **No hidden configuration.** Anything git-ignored that the demo needs
   (`AIProviders.json`, API keys, local paths) breaks for attendees.
   Prefer local, keyless services (`4dembeddings`); otherwise document the
   exact file to create.
4. **Components** through `dependencies.json` only, pinned to released
   versions; never commit `Components/` builds.
5. **Opens into the demo.** `On Startup` opens the main form directly; no
   splash, no menu hunt. Show progress and readiness **in the form**
   (status line, disabled actions until ready), not in alerts.
6. **First-launch downloads** (models, data) show size and progress, go
   to a stable per-user cache (e.g. `~/.GGUF/<repo>`), and are reused on
   later launches.
7. **Language.** UI follows the OS language, en + ja XLIFF (`4dlocalise`).
   Decide separately whether the **data** and sample inputs are localised.
8. **Clean up.** Remove scratch or destructive methods (e.g. one that nulls
   every vector and ends with `TRACE`), French or other locale leftovers in
   `menus.json`/`folders.json`, and vendored `.agents/skills` copies.
9. **Skills submodule.** `.agents` is the `dist` branch of miyako/skills
   (see the repository README); never edit inside `.agents`. Add
   `.github/workflows/update-skills.yml` (weekly bump of the submodule
   pointer) and `copilot-setup-steps.yml` with `submodules: true`.
   Templates: `references/workflows.md`.
10. **README** (`references/readme.md`).
11. **Verify like an attendee:** fresh clone in a temp folder, data from
    the release, open, first launch, search, quit; no orphan processes
    afterwards (`4dcli`, `references/shared-desktop.md`).

## Checklist

- [ ] compatibilityVersion = target release = README badge
- [ ] Runs from a fresh clone + documented release download only
- [ ] Opens straight into the demo form; status shown in the form
- [ ] UI in the OS language (en/ja); data-language decision recorded
- [ ] No scratch methods, locale leftovers or vendored skills
- [ ] `.agents` submodule on `dist` + update workflow
- [ ] README follows `references/readme.md`
- [ ] No orphan helper processes after quit
