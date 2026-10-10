---
name: 4dmodernise
description: >
  Modernise legacy 4D code: replace C_* declarations (C_LONGINT, C_TEXT,
  C_OBJECT...) with var and #DECLARE, clean Compiler_Methods /
  Compiler_Variables, and replace deprecated or compatibility-layer commands
  (_o_ / _O_ prefixes, _O_PLATFORM PROPERTIES, OBJECT SET ACTION with
  _o_Object Accept action) with their modern equivalents. Use when upgrading
  or auditing an older 4D project.
---

# 4D Modernise

## Scope

Rewriting **existing** 4D code that uses deprecated syntax or commands so
that it matches what current 4D expects:

* `C_*` declaration commands → `var` and `#DECLARE` (4D 20 R7+)
* `Compiler_Methods.4dm` / `Compiler_Variables.4dm` cleanup
* `_o_` / `_O_` compatibility-layer commands and other deprecated commands
  → modern commands or declarative form properties

Every modernisation starts by reading the project's `compatibilityVersion`
("4D Version Detection" in `skills/4dproject/SKILL.md`): a replacement can
only be used if it exists in the version the project targets. Any project in
`.4DProject` form is v17 or later, so version checks against older releases
are dead code.

### Not in this skill

| Topic | Skill |
|---|---|
| Version detection, token suffix rules | `4dproject` |
| `Get localized string` → `Localized string`, XLIFF | `4dlocalise` |
| `New process` + blocking `DIALOG` startup patterns | `4dstartup` |
| Method wrappers in `menus.json` → standard actions | `4dproject` (`references/menus.md`) |
| Method attributes (`invisible`, `shared`, ...) | `4dmethods` |
| Checking that rewritten `.4dm` is valid | `4dlsp` |
| Looking up a command's current signature | `4dlang` |

## Route Table

| Task involves | Open |
|---|---|
| `C_LONGINT`, `C_TEXT`, ... `C_*($1)`, `$0`, `Compiler_*` methods | `references/declarations.md` |
| `_o_` / `_O_` commands, `_O_PLATFORM PROPERTIES`, `OBJECT SET ACTION` with `_o_` constants, other deprecated commands | `references/deprecated-commands.md` |

## Workflow

1. Detect the project version (`4dproject`).
2. Grep for the legacy patterns listed in the reference file for the task.
3. Replace the **command name and call pattern**, never only the token.
   Write replacement commands without token suffixes unless the exact
   `Name:Cnnn` string already exists in the project (token rules in
   `skills/4dproject/SKILL.md`).
4. Validate every changed `.4dm` file with `4dlsp`.
5. Run the project's own tests or compile step if it has one (see "Syntax
   checking vs running code" in `skills/4dlsp/SKILL.md`).
