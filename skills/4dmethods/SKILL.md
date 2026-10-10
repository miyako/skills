---
name: 4dmethods
description: >
  4D project method attributes and visibility: the //%attributes = {...}
  first line of .4dm method files (invisible, preemptive, shared,
  publishedWeb/Soap/Wsdl/Sql, executedOnServer), METHOD GET/SET ATTRIBUTES,
  and when to hide subroutines, Form-dependent and callback methods from the
  Run Method dialog. Use when creating project methods or auditing which
  methods should be invisible.
---

# 4D Method Attributes & Visibility

## Scope

Attributes of **project methods** (`Project/Sources/Methods/*.4dm`) and the
rule for which methods appear in the **Run > Method...** dialog.

Every project method is visible in that dialog by default. Many methods are
not designed for standalone execution -- subroutines, form-dependent helpers,
callbacks -- and fail when run from it. The `invisible` attribute hides a
method from the dialog while keeping it callable from code, forms and menus.

A method that needs `#DECLARE` parameters is almost always a subroutine.
When migrating `C_*($1)` to `#DECLARE` (`4dmodernise` skill), audit its
visibility at the same time, and vice versa.

### Not in this skill

| Topic | Skill |
|---|---|
| `C_*` → `#DECLARE` | `4dmodernise` |
| `menus.json` method vs standard action | `4dproject` (`references/menus.md`) |
| Checking `.4dm` syntax | `4dlsp` |
| Class functions (`Function`, `shared`/`singleton` keywords) | `4dlang` |

References:
- Project method properties: https://developer.4d.com/docs/Project/project-method-properties
- `METHOD SET CODE` (attribute metadata): https://developer.4d.com/docs/commands/method-set-code
- `METHOD SET ATTRIBUTES` / `METHOD GET ATTRIBUTES`: https://developer.4d.com/docs/commands/method-set-attributes
- Preemptive processes: https://developer.4d.com/docs/Develop/preemptive-processes
- Components (shared methods): https://developer.4d.com/docs/Extensions/develop-components

## When to Make a Method Invisible

A project method **must** be marked invisible if any of the following apply:

### 1. It references `Form`

Methods that use the `Form` command require a current form context. They will fail or return `Null` when executed standalone.

**Indicators:**
- Direct use of `Form`
- Access to `Form.propertyName`
- Passing `Form` as a parameter

### 2. It is a subroutine called exclusively from other methods or forms

Methods that serve as helpers, utilities, or callbacks — never intended to be run directly by the developer.

**Indicators:**
- Called via `MethodName(params)` from other methods
- Called via `CALL WORKER`, `CALL FORM`, `Formula(MethodName)`
- Has `#DECLARE` with required parameters (will fail without them)
- Never appears as a menu method in `menus.json`

### 3. It references `FORM Event`

Methods that inspect `FORM Event` depend on being called within a form event cycle.

### 4. It uses form object commands with `*` (named reference)

Methods using `OBJECT SET` / `OBJECT GET` commands with the `*` operator and object name strings depend on a form being displayed.

**Indicators:**
- `OBJECT SET TITLE(*; "objectName"; ...)`
- `OBJECT SET VALUE(*; "objectName"; ...)`
- `OBJECT GET RGB COLORS(*; "objectName"; ...)`
- Any `OBJECT` command with `*` as first parameter

### 5. It is a callback or worker handler

Methods designed to be invoked via `CALL WORKER` or `CALL FORM` with specific parameters.


## When to Keep a Method Visible

A method should remain visible (the default) if:

- It is a **tool** or **utility** designed to be run from the Run Method dialog
- It is a **startup method** (e.g., `00_Start`) that serves as an entry point
- It is a **menu method** referenced in `menus.json`
- It is a **standalone test** or **demo** method


## How Method Attributes Work in Project Mode

### Source-Level Attributes (`.4dm` files)

In project mode, method attributes are stored as a JSON comment on the **first line** of the `.4dm` source file:

```4d
//%attributes = {"invisible":true}
```

This line is parsed by 4D at load time. It is **not** a regular comment — the `//%attributes = ` prefix is a reserved marker.

### Attribute Format

The first line must match this exact pattern:

```
//%attributes = {JSON_OBJECT}
```

- The prefix `//%attributes = ` is **literal and required** (note the spaces around `=`)
- The JSON object contains key-value pairs for each attribute
- Only attributes that differ from defaults need to be specified

### Empty vs Populated Attributes

| First line | Meaning |
|-----------|---------|
| `//%attributes = {}` | All defaults (method is visible, cooperative, etc.) |
| `//%attributes = {"invisible":true}` | Hidden from Run dialog |
| `//%attributes = {"invisible":true,"preemptive":"capable"}` | Hidden + preemptive-capable |
| *(no first line / missing)* | All defaults |

### Supported Attribute Keys

These are the keys accepted by `METHOD SET ATTRIBUTES`. Explorer folders
are not a method attribute -- they live in `Project/Sources/folders.json`
(see `skills/4dproject/references/layout.md`).

| Key | Type | Default | Purpose |
|-----|------|---------|---------|
| `invisible` | Boolean | `false` | Hide from Run > Method… dialog |
| `preemptive` | String | `"indifferent"` | Thread safety: `"capable"`, `"incapable"`, or `"indifferent"` |
| `publishedWeb` | Boolean | `false` | Available via 4DACTION URLs and tags |
| `publishedSoap` | Boolean | `false` | Published as SOAP Web Service |
| `publishedWsdl` | Boolean | `false` | Included in WSDL |
| `shared` | Boolean | `false` | Shared between host and components |
| `publishedSql` | Boolean | `false` | Callable from SQL engine |
| `executedOnServer` | Boolean | `false` | Always execute on server (client-server) |
| `lang` | String | *(none)* | Written by the IDE in source files (e.g. `"en"`); preserve it, never add or change it |

### Programmatic Access

Attributes can also be read and set at runtime:

```4d
// Reading attributes
var $attr : Object
METHOD GET ATTRIBUTES("MyMethod"; $attr)

// Setting attributes
var $attr : Object
$attr:=New object("invisible"; True)
METHOD SET ATTRIBUTES("MyMethod"; $attr)
```

When using `METHOD SET CODE` to create or modify methods programmatically, the attributes line is parsed from the first line of the code text:

```4d
var $code : Text
$code:="//%attributes = {\"invisible\":true}\n#DECLARE($param : Text)\n// method body"
METHOD SET CODE("MyMethod"; $code)
```


## Audit Procedure

When reviewing a 4D project for correct method visibility, follow this procedure:

### Step 1: List all project methods

Scan `Project/Sources/Methods/*.4dm` for all project method files.

### Step 2: Check each method's first line

Read the first line and parse the attributes JSON:
- If the line starts with `//%attributes = `, parse the JSON
- If the line is absent or the JSON is `{}`, the method uses all defaults (visible)

### Step 3: Analyse method content

For each visible method, scan the body for indicators that it requires a calling context:

| Pattern to search | Implies |
|-------------------|---------|
| `Form` used as a command | Requires form context |
| `Form.` (property access on Form object) | Requires form context |
| `FORM Event` or `FORM Event` | Requires form event cycle |
| `OBJECT SET ` / `OBJECT GET ` with `*` | Requires displayed form |
| `#DECLARE(` with required parameters | Subroutine (needs caller) |
| `Current form window` | Requires form context |

### Step 4: Cross-reference with entry points

Check whether the method is referenced as:
- A menu method in `Project/Sources/menus.json`
- A startup method (`onStartup.4dm` calls it)
- A button/object method via `form.4DForm`

Methods that are **only** called from other methods or forms (never as a top-level entry point) should be invisible.

### Step 5: Update attributes

For methods that should be invisible, modify the first line:

**If the method already has an attributes line:**
```4d
// Before
//%attributes = {}

// After
//%attributes = {"invisible":true}
```

**If the method has an attributes line with other attributes:**
```4d
// Before
//%attributes = {"preemptive":"capable"}

// After
//%attributes = {"invisible":true,"preemptive":"capable"}
```

**If the method has no attributes line:**
Insert as the new first line:
```4d
//%attributes = {"invisible":true}
```


## Anti-Patterns to Avoid

### ❌ Making startup or menu methods invisible

```4d
// WRONG — 00_Start is a top-level entry point, keep it visible
//%attributes = {"invisible":true}
```

**Why:** Startup methods and menu methods are designed to be run manually during development. Hiding them makes debugging harder.

### ❌ Leaving subroutines visible

```4d
// WRONG — this method uses Form and will crash if run standalone
//%attributes = {}
#DECLARE($options : Object)
Form.result:=$options.value
```

**Why:** A developer selecting this from Run > Method… will get an error. Mark it invisible.

### ❌ Forgetting the attributes line entirely

When creating new methods programmatically or manually, always include the attributes line. Omitting it uses defaults (visible), which may not be appropriate for subroutines.

### ❌ Malformed attributes line

```4d
// WRONG — missing space around =
//%attributes={"invisible":true}

// WRONG — not valid JSON
//%attributes = {invisible:true}

// WRONG — wrong prefix
// %attributes = {"invisible":true}
```

The format is strict. The prefix must be exactly `//%attributes = ` followed by valid JSON.

### ❌ Using `invisible` to hide methods from programmers

The `invisible` attribute only affects the **Run > Method…** dialog. Invisible methods are still:
- Listed in the Explorer
- Visible in the Code Editor
- Callable from any other method
- Searchable in Find/Replace

Do not use `invisible` as a security or access-control mechanism.


## Relationship to Other Method Properties

### Available Through (Web, SOAP, SQL, REST)

The `publishedWeb`, `publishedSoap`, `publishedSql` attributes control whether external services can call the method. These are **independent** of `invisible`:

- A method can be invisible (hidden from Run dialog) but published as a web service
- A method can be visible but not published for any external service

**Default security posture:** All `published*` attributes default to `false`. Only explicitly enable them for methods that need external access.

### Execute on Server

The `executedOnServer` attribute forces client-server execution on the server machine. This is independent of visibility.

### Preemptive Mode

The `preemptive` attribute declares thread safety. It is independent of visibility but important for methods called in preemptive contexts:

| Value | Meaning |
|-------|---------|
| `"indifferent"` | 4D decides based on content analysis (default) |
| `"capable"` | Developer declares the method is thread-safe |
| `"incapable"` | Developer declares the method is NOT thread-safe |

### Shared (Components)

The `shared` attribute controls whether a method is accessible across the host/component boundary. An invisible shared method is hidden from the Run dialog but still callable by the host or component.


## Batch Operations

### In the 4D IDE

Use **Explorer > Methods > Options > Batch setting of attributes…** to modify attributes for groups of methods matching a wildcard pattern (using `@`):

- `helper@` — methods starting with "helper"
- `@_internal` — methods ending with "_internal"
- `@util@` — methods containing "util"

### Programmatically

Use arrays with `METHOD SET ATTRIBUTES`:

```4d
ARRAY TEXT($paths; 0)
ARRAY OBJECT($attrs; 0)

// Collect method paths and build attribute objects
// ...

METHOD SET ATTRIBUTES($paths; $attrs)
```

### In Source Control (Project Mode)

Since attributes are stored in the first line of `.4dm` files, they can be audited and modified using standard text processing tools (grep, sed, scripting) as part of a CI/CD pipeline or code review process.


## Checklist

When auditing method visibility in a 4D project:

- [ ] All methods referencing `Form` are marked invisible
- [ ] All methods referencing `FORM Event` are marked invisible
- [ ] All methods using `OBJECT` commands with `*` named references are marked invisible
- [ ] All subroutines with required `#DECLARE` parameters are marked invisible
- [ ] Every changed `.4dm` still parses (`4dlsp`)
- [ ] All callback/worker handler methods are marked invisible
- [ ] Startup methods (`00_Start`, etc.) remain visible
- [ ] Menu methods referenced in `menus.json` remain visible
- [ ] Standalone tools and utilities remain visible
- [ ] The `//%attributes = ` format is syntactically correct on every modified method
- [ ] Existing attributes (e.g., `preemptive`, `lang`) are preserved when adding `invisible`
- [ ] No `published*` attributes were accidentally changed
