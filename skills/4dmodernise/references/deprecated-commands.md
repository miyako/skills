# Deprecated Commands

References:
- 4D command reference (check each page for a "Deprecated" notice): https://developer.4d.com/docs/commands/
- `Is macOS`: https://developer.4d.com/docs/commands/is-macos
- `Is Windows`: https://developer.4d.com/docs/commands/is-windows
- Simplified commands for cleaner codebase: https://blog.4d.com/simplified-commands-for-cleaner-codebase/
- Standard actions: https://developer.4d.com/docs/Desktop/standard-actions

4D keeps old commands available under "compatibility" names long after a
modern replacement exists. Any project in `.4DProject` form runs on **4D v17
or later** (binary-to-project conversion does not exist for earlier
versions), so **any command whose replacement shipped in v17 or earlier can
be migrated unconditionally**. Replacements introduced later (e.g. 20 R7)
depend on the project version -- see "4D Version Detection" in
`skills/4dproject/SKILL.md`.

## Recognising Deprecated Commands

### The `_o_` / `_O_` naming convention

Commands prefixed with `_o_` or `_O_` (case varies by command) are 4D's internal
**compatibility layer** — old command implementations kept solely so pre-existing compiled
code keeps working. They are never the preferred spelling for new or updated code.

**Indicators a command is part of the compatibility layer:**
- The command name starts with `_o_` or `_O_` (e.g. `_o_Object Accept action`,
  `_O_PLATFORM PROPERTIES`, `_O_REDRAW LIST`).
- The 4D documentation page for the command is titled or tagged "deprecated" and links to
  a "replaced by" command.
- The command only appears in old/unconverted code, never in current 4D sample code or
  blog posts.

### Other deprecation signals

Not all deprecated commands use the `_o_`/`_O_` prefix. Also watch for:
- Commands explicitly called out in 4D's "Simplified commands for cleaner codebase" blog
  post (see References) — e.g. `Get localized string` → `Localized string`.
- Constants used only to emulate behaviour now exposed directly as a boolean command (e.g.
  comparing a platform code constant instead of calling a dedicated `Is <Platform>`
  command).
- Commands whose 4D documentation page has a "Deprecated" banner or redirects to another
  command's page.

---

## Known Deprecated Commands and Replacements

| Deprecated | Replacement | Notes |
|---|---|---|
| `_O_PLATFORM PROPERTIES` | `Is macOS`, `Is Windows` | Returned a platform code via a parameter; branch on the boolean directly. |
| `OBJECT SET ACTION` with `_o_Object Accept action` / `_o_Object Cancel action` | `"action": "accept"` / `"action": "cancel"` on the object in `form.4DForm` | Declarative standard actions get native enable/disable behaviour. |
| `Get localized string` | `Localized string` | 20 R7+. See the `4dlocalise` skill. |
| `C_LONGINT`, `C_TEXT`, ... `C_COLLECTION` | `var` / `#DECLARE` | 20 R7+. See `declarations.md`. |
| `New process` used only to get an event cycle for a dialog | `CALL WORKER(1; ...)` + `DIALOG(...; *)` | An obsolete pattern rather than a renamed command. See the `4dstartup` skill. |
| Menu methods that wrap one command (`m_Quit` → `QUIT 4D`) | `"action"` in `menus.json` | See `references/menus.md` in the `4dproject` skill. |

> This table is **not exhaustive**. Check the command's page on
> `https://developer.4d.com/docs/commands/` for a "Deprecated" notice (or
> look it up with the `4dlang` skill) before assuming a command is current,
> especially anything with an `_o_`/`_O_` prefix.

## Migration Rules

### Rule 1: Replace platform-code comparisons with `Is <Platform>`

**Before:**
```4d
var $platform : Integer
_O_PLATFORM PROPERTIES($platform)

Case of 
	: ($platform=Mac OS)
		// mac-specific code
	: ($platform=Windows)
		// windows-specific code
End case 
```

**After:**
```4d
If (Is macOS)
	// mac-specific code
Else 
	// windows-specific code
End if 
```

**Key points:**
- `Is macOS` and `Is Windows` are plain boolean commands — no output parameter, no
  constant comparison, no `Case of` needed for a two-platform branch.
- Drop the now-unused `$platform` variable declaration entirely; do not leave an unused
  `var` line behind.
- If the code only ever branched on two platforms (mac/Windows), an `If`/`Else` is
  clearer than a `Case of`. Keep `Case of` only when there are more than two branches.

### Rule 2: Prefer declarative `"action"` in form JSON over `OBJECT SET ACTION` with `_o_` constants

**Before:**
```4d
OBJECT SET ACTION(*; "btnOK"; _o_Object Accept action)
```

**After:**
```json
"btnOK": {
	"type": "button",
	"action": "accept",
	...
}
```

**Why:** Setting the standard action in the form JSON gives the button native
enable/disable behaviour without any method code, and removes the need for the `*`
named-object-reference call (which also requires the method to be marked `invisible` -- see the
`4dmethods` skill). Only use `OBJECT SET ACTION` at runtime when the
action must be assigned conditionally based on logic that cannot be expressed statically
in the form.

### Rule 3: Do not "fix" a deprecated command by swapping tokens only

Renaming a command's token without changing the command name and call pattern is not a
migration — it is guessing, which the token rules in `skills/4dproject/SKILL.md` forbid. Always replace the
**command name and its parameter signature**, matching the modern command's actual
signature (e.g. `Is macOS` takes no parameters and returns a boolean, unlike
`_O_PLATFORM PROPERTIES` which writes into a longint parameter).

---

## Audit Procedure

### Step 1: Search for compatibility-layer commands

```
grep -rn "_[oO]_[A-Za-z]" Project/Sources --include=*.4dm
```

Any match is a candidate for migration — confirm the modern replacement on
`https://developer.4d.com/docs/commands/` before changing anything.

### Step 2: Route the dedicated cases

Some deprecations have their own owner and are handled there, not here:
- `C_*` declarations → `declarations.md`
- `Get localized string` → the `4dlocalise` skill
- Blocking `DIALOG` + `CLOSE WINDOW` + `New process` startup patterns → the `4dstartup` skill

### Step 3: Verify no non-variable / no-parameter mismatches remain

After replacing a command, re-read the full method to confirm:
- Any variable that only existed to hold the deprecated command's output parameter
  (e.g. `$platform`) is removed if no longer read elsewhere.
- Any `Case of` / `If` structure that branched on a returned constant now branches on the
  new boolean command directly, without a leftover comparison against the constant.

### Step 4: Confirm nothing regressed

Validate every changed `.4dm` with the `4dlsp` skill (`hover` the replacement commands
if in doubt), run the project's own build/test step if any, and trace each call site of
the removed command to confirm behaviour is preserved.

---

## Anti-Patterns to Avoid

### ❌ Leaving the output parameter and `Case of` in place

```4d
// WRONG — still declares $platform and branches on constants, only the fetch command changed
var $platform : Integer
If (Is macOS)
	$platform:=Mac OS
End if 
Case of 
	: ($platform=Mac OS)
		...
End case 
```

**Why:** This defeats the purpose of the simplification. Branch on the boolean command
directly.

### ❌ Guessing a token for the replacement command

```4d
// WRONG — a token typed from memory
Is macOS:C9999
```

**Why:** Never invent token numbers (token rules in `skills/4dproject/SKILL.md`). Omit
the token; 4D resolves the plain name and adds the correct token on save.

### ❌ Assuming every `_o_`/`_O_`-prefixed command has a direct one-line replacement

**Why:** Some compatibility commands map to a completely different mechanism (e.g.
`_o_Object Accept action` maps to a form JSON property, not another method-level command).
Always check what category of replacement applies — command-for-command, or
command-for-declarative-property — before editing.

### ❌ Silently keeping deprecated commands "because they still work"

**Why:** Deprecated commands may be removed in a future 4D version, and they are
excluded from new documentation and examples, making the code harder to maintain. If a
project's `compatibilityVersion` already implies a modern floor (v17+, or 20 R7+ for
`C_*`/`Get localized string`), there is no compatibility reason left to keep the legacy
form.

---

## Checklist

- [ ] Searched for `_o_`/`_O_`-prefixed commands across all `.4dm` files
- [ ] Each match's replacement confirmed on the 4D command reference (not guessed)
- [ ] Output-parameter variables removed once no longer needed (e.g. `$platform`)
- [ ] `Case of` / constant comparisons simplified to direct boolean checks where the
      replacement command is a boolean (e.g. `Is macOS`, `Is Windows`)
- [ ] Declarative `"action"` used in form JSON instead of `OBJECT SET ACTION` with `_o_`
      constants, where the action can be expressed statically
- [ ] No invented/guessed tokens introduced on replacement commands
- [ ] `C_*`, `Get localized string` and startup-pattern cases handled by their owners
      (`declarations.md`, `4dlocalise`, `4dstartup`)
