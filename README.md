# skills

[Agent Skills](https://agentskills.io/home) for 4D development.

The skillset lives in [`4d-skills/`](4d-skills): a root
[`AGENTS.md`](4d-skills/AGENTS.md) that routes tasks to skills, one folder
per skill under [`4d-skills/skills/`](4d-skills/skills) (each with a
`SKILL.md`), and the validation schemas under
[`4d-skills/schemas/`](4d-skills/schemas). Every topic has exactly one
owning skill; the others link to it.

## Skills

### 4D artifacts and tooling

| Skill | Scope |
|---|---|
| [`4dproject`](4d-skills/skills/4dproject/SKILL.md) | The project as a whole: `.4DProject`, version detection, token suffixes, folder layout, `menus.json`, the canonical `.gitignore` |
| [`4dcatalog`](4d-skills/skills/4dcatalog/SKILL.md) | `.4DCatalog` database schema: structure, DTD validation, diagrams |
| [`4dform`](4d-skills/skills/4dform/SKILL.md) | `.4DForm` JSON: objects, list box defaults, layout geometry and overlap checks, form documentation index, schema validation |
| [`4dsettings`](4d-skills/skills/4dsettings/SKILL.md) | `.4DSettings` (placeholder) |
| [`4dlsp`](4d-skills/skills/4dlsp/SKILL.md) | `.4dm` validation, syntax check and code intelligence with `tool4d-lsp-stdio` |
| [`4dlang`](4d-skills/skills/4dlang/SKILL.md) | Classic command and OOP class member lookup; documentation and forum search |
| [`4dcli`](4d-skills/skills/4dcli/SKILL.md) | Running tool4d / 4D from the command line: tests, compile, form rendering |
| [`4dtools`](4d-skills/skills/4dtools/SKILL.md) | Provisioning the helper binaries the other skills use |

### 4D development topics

| Skill | Scope |
|---|---|
| [`4dmethods`](4d-skills/skills/4dmethods/SKILL.md) | Method attributes and which methods to hide from the Run Method dialog |
| [`4dmodernise`](4d-skills/skills/4dmodernise/SKILL.md) | `C_*` → `var` / `#DECLARE`, deprecated `_o_` commands and their replacements |
| [`4dcss`](4d-skills/skills/4dcss/SKILL.md) | Form stylesheets, dark mode, Liquid Glass / Fluent UI form themes |
| [`4dlocalise`](4d-skills/skills/4dlocalise/SKILL.md) | XLIFF localisation, `Localized string`, attributes that follow the UI language |
| [`4dstartup`](4d-skills/skills/4dstartup/SKILL.md) | The non-blocking startup window pattern and chaining forms |
| [`4daikit`](4d-skills/skills/4daikit/SKILL.md) | 4D AI Kit: chat, vision, async callbacks and streaming |
| [`4dorda`](4d-skills/skills/4dorda/SKILL.md) | ORDA queries and placeholders, null handling, saving and locking, `fromCollection`, vector similarity |

### Technote-localisation repositories only

Used only in repositories created from
[4d-technote-localisation-template](https://github.com/miyako/4d-technote-localisation-template)
(a `technote.json` at the root).

| Skill | Scope |
|---|---|
| [`technote-localise-4d-project`](4d-skills/skills/technote-localise-4d-project/SKILL.md) | Localising the 4D demo under `demo/` |
| [`technote-apply-glossary`](4d-skills/skills/technote-apply-glossary/SKILL.md) | Changing a term across glossary, text and figures |
| [`technote-review-figures`](4d-skills/skills/technote-review-figures/SKILL.md) | Reviewing and fixing localised figures |
| [`technote-localise-demo-data`](4d-skills/skills/technote-localise-demo-data/SKILL.md) | Replacing the demo's sample data and recomputing the examples |
| [`technote-release`](4d-skills/skills/technote-release/SKILL.md) | Publishing the PDF and demo zip as a GitHub release |

## Using the skills in a 4D repository

The [`dist`](https://github.com/miyako/skills/tree/dist) branch contains
only the skillset: the content of `4d-skills/` at its root (`AGENTS.md`,
`skills/`, `schemas/`, `MIGRATION.json`) plus this README and `VERSION`.
It is published automatically from `main` by
[`publish-dist.yml`](https://github.com/miyako/skills/blob/main/.github/workflows/publish-dist.yml).
Add it as a submodule at `.agents`:

```sh
git submodule add -b dist https://github.com/miyako/skills.git .agents
```

After cloning a repository that already has it:

```sh
git submodule update --init .agents
```

(`--recursive` is not needed: the `dist` branch has no submodules.) To pick
up a newer skillset, run `git submodule update --remote .agents` and commit
the new submodule commit.

Once mounted:

* skills live at `.agents/skills/<name>/SKILL.md`, where agent hosts that
  scan `.agents/skills/` discover them;
* schemas live at `.agents/schemas/`;
* `.agents/AGENTS.md` holds the skill-selection table. Point to it from the
  repository's own root `AGENTS.md` (e.g. "For 4D work, read
  `.agents/AGENTS.md` and the skills under `.agents/skills/`"), since a
  nested `AGENTS.md` is not read automatically;
* tools provisioned by `4dtools` still go under the **consumer** repository's
  `tools/<skill>/` (e.g. `tools/4dlsp/`), never inside `.agents/`. Git-ignore
  only those directories, not the whole `tools/` folder -- see
  [`4dproject`](4d-skills/skills/4dproject/SKILL.md) for the canonical
  `.gitignore`.

## Migration from `.github/instructions`

Many 4D repositories used to carry copies of the same
`.github/instructions/*.instructions.md` files and `.github/skills/`
folders. Their generic 4D content now lives in the skills above;
repository-specific rules stay in each repository.
[`4d-skills/MIGRATION.json`](4d-skills/MIGRATION.json) maps every old file to
its new home (`instructions.<file>.status`: `skill`, `instruction` or
`deleted`; legacy `.github/skills/` folders are under `skills`).

| Old file | New home |
|---|---|
| `variable.declarations`, `deprecated.commands` | `4dmodernise` |
| `method.visibility` | `4dmethods` |
| `menu` | `4dproject` |
| `listbox` | `4dform` |
| `css`, `tahoe.css` | `4dcss` |
| `localisation` | `4dlocalise` |
| `aikit.async` | `4daikit` |
| `startup` | `4dstartup` (generic pattern); HDI splash specifics stay as `.github/instructions/hdi.startup.instructions.md` |
| `4d-docs`, `4d-form-layout` skills | `4dform` (doc index, layout, `form_layout_calc.py`); search fallback in `4dlang` |
| `apply-glossary`, `review-figures`, `localise-demo-data`, `release-technote`, `localise-4d-project` skills | `technote-*` skills (generic 4D parts of `localise-4d-project` → `4dlocalise` and the other 4D skills) |
| `readme.structure`, `readme.branches`, `technote-translation` | Stay in their repositories under `.github/instructions/` |
| `copilot-instructions.md` | The repository's root `AGENTS.md` |
| `readme.usage.guidance`, `readme.hdi` | Deleted |
