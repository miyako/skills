---
name: 4dform
description: >
  Design, modify, and validate 4D Form source files (.4DForm): form and
  object JSON structure, per-object reference material, the authoring
  protocol to follow, and schema validation against the 4D Form schema.
---

# 4D Form

## Scope

This skill covers 4D Form source files:

* `*.4DForm`

A `.4DForm` file is a 4D-specific JSON artifact.

Do not treat a `.4DForm` as generic JSON. Generic JSON validity is necessary
but is not sufficient to establish that the artifact is a valid 4D Form.

This skill owns form design as well as form validation. Object-level
knowledge lives in `references/` and is loaded on demand -- see the route
table below.

### Not in this skill

* `.4dm` code validation -- `skills/4dlsp/SKILL.md`
* 4D command and OOP class syntax -- `skills/4dlang/SKILL.md`
* project layout, `.gitignore`, `menus.json`, `roles.json` --
  `Project/AGENTS.md`
* `compatibilityVersion` and `tokenizedText` -- `skills/4dproject/SKILL.md`
* running tool4d or 4D from a shell -- `skills/4dcli/SKILL.md`
* provisioning `boon` and the other helper binaries --
  `skills/4dtools/SKILL.md`

## Authoring Protocol

Follow these four phases in order. Announce the phase before each action,
for example:

```
PHASE: BUILD -- creating Forms/Login/form.4DForm
```

The announcement is not decoration. If you cannot name the phase you are
in, you have drifted, and drifting into open-ended exploration is the
known failure mode for this task.

### PHASE: ROUTE (one step)

Read the route table below. Name the reference file(s) the task needs.
Do not open them yet. Do not list directories to "understand the
structure" -- the structure is fixed and is given in this file.

### PHASE: READ (hard cap)

Read each selected file **exactly once**. Then stop reading.

The reading budget for a whole task is:

* `references/form-concepts.md` -- once, for any form work
* one file from `references/objects/` per object type in the task
* `references/property-reference.md` -- only when resolving a specific
  property name you could not resolve from the object file
* `references/screenshot-rendering.md` -- only when rendering a capture

You will never need more than three reference files for a single-object
task. There is no prerequisite chain to follow and nothing to remember
across turns: if you lose context, re-enter at PHASE: ROUTE and read the
one file the current object needs.

### PHASE: BUILD

Create the files. Start from the skeleton below rather than from an empty
buffer:

```
Project/Sources/Forms/<FormName>/form.4DForm
Project/Sources/Forms/<FormName>/method.4dm                    (if the form has a form method)
Project/Sources/Forms/<FormName>/ObjectMethods/<Object>.4dm    (per wired object)
```

### PHASE: VALIDATE

Run the done-gate below. The task is not finished until it passes.

## Stuck Detector

Any of these means **stop researching and start building**:

* You are about to read a file you have already read.
* You are about to list a directory you have already listed.
* You are about to list a directory "to understand the structure".
* Three consecutive reads or lists have happened with no file write
  between them.
* Your last message began with "Let me look at", "Let me examine", or any
  other phrase that describes looking rather than doing.

The recovery is always the same: go to PHASE: BUILD, write the skeleton to
disk, and fill it in from there.

## Starting Skeleton

**START FROM THIS -- fill in the objects.** Write it to
`Project/Sources/Forms/<FormName>/form.4DForm`, then add objects to
`pages[1].objects`.

```json
{
  "$4d": {
    "version": "1",
    "kind": "form"
  },
  "windowSizingX": "variable",
  "windowSizingY": "variable",
  "windowMinWidth": 0,
  "windowMinHeight": 0,
  "windowMaxWidth": 32767,
  "windowMaxHeight": 32767,
  "rightMargin": 20,
  "bottomMargin": 20,
  "events": ["onLoad", "onUnload"],
  "windowTitle": "window title",
  "destination": "detailScreen",
  "method": "method.4dm",
  "pages": [
    { "objects": {} },
    {
      "objects": {
        "myButton": {
          "type": "button",
          "left": 20,
          "top": 20,
          "width": 100,
          "height": 24,
          "text": "OK",
          "method": "ObjectMethods/myButton.4dm",
          "events": ["onClick"]
        }
      }
    }
  ]
}
```

Each of these is a real failure if omitted:

* `pages` needs at least two entries. Index 0 is always visible; index 1
  is the first real page.
* `top` and `left` are required on every object.
* `"method": "method.4dm"` is what binds the form method. Creating the
  file at the conventional path is not enough -- without this property
  `On Load` never fires and the code is silently dead.
* `"method": "ObjectMethods/<Object>.4dm"` is what binds an object method,
  and `"events"` is what lets it receive anything.

## Route Table

Open only the file for the object(s) the task touches.

| Task involves | Open |
|---|---|
| Form structure: pages, events, window sizing, entry order, form class, data sources, CSS, fonts, icons | `references/form-concepts.md` |
| Button | `references/objects/button.md` |
| Checkbox / three-state | `references/objects/checkbox.md` |
| Radio button / radioGroup | `references/objects/radio-button.md` |
| Button grid | `references/objects/button-grid.md` |
| Picture button (animated / frame-based) | `references/objects/picture-button.md` |
| Splitter | `references/objects/splitter.md` |
| Ruler | `references/objects/ruler.md` |
| Stepper | `references/objects/stepper.md` |
| Progress indicator / thermometer | `references/objects/progress-indicator.md` |
| Spinner | `references/objects/spinner.md` |
| Rectangle shape | `references/objects/rectangle.md` |
| Line shape | `references/objects/line.md` |
| Oval shape | `references/objects/oval.md` |
| Static picture | `references/objects/picture.md` |
| Dropdown list | `references/objects/dropdown.md` |
| Combo box | `references/objects/combo.md` |
| Picture pop-up menu | `references/objects/picture-popup.md` |
| Tab control | `references/objects/tab.md` |
| Group box | `references/objects/group-box.md` |
| Input / field / text entry | `references/objects/input.md` |
| Static text / label / rotation / dynamic reference | `references/objects/text.md` |
| Hierarchical list / tree / ListRef / choice list | `references/objects/list.md` |
| Picture input: interactive SVG, mouse tracking, clickable map, drawing tool | `references/objects/picture-input.md` |
| SVG rendering engine: supported elements, filters, `SVG SET ATTRIBUTE` | `references/objects/svg-rendering.md` |
| Resolving a property name: JSON key, CSS name, getter/setter command | `references/property-reference.md` |
| What a `FORM SCREENSHOT` or printed capture actually shows | `references/screenshot-rendering.md` |

If a task spans several objects, open the files for exactly those objects.
Do not open unrelated files "just in case".

Each reference file carries `object`, `json_type`, `keywords`, and
`summary` front matter. Skim that to confirm relevance; it is not a
substitute for reading the body of the file you selected.

## Definition of Done

A form task is complete when all three hold. Report each explicitly.

1. **Schema validation passes** for every `.4DForm` written or modified:

   ```sh
   tools/4dform/boon schemas/4dform/formsSchema.json <form.4DForm>
   ```

2. **`.4dm` validation reports no errors** for every form method and
   object method written or modified (exit code `0`):

   ```sh
   tools/4dlsp/tool4d-lsp-stdio validate --workspace Project/ <each .4dm>
   ```

3. **Every `ObjectMethods/*.4dm` is referenced by a `"method"` property**
   in the form JSON, and the object also declares the `"events"` it needs.

Step 3 is a manual check: there is no validator for it. An orphaned object
method produces no error at all -- it is simply never called, so the form
appears to load correctly and does nothing. Enumerate the files under
`ObjectMethods/` and find each one in the form JSON.

The two validators are not interchangeable. Schema validation gates the
artifact; `.4dm` validation gates the code. Both must pass and neither is
sufficient alone. `jq empty` is not schema validation and does not count
toward any of the three.

## Schema

The 4D Form schema is:

```
schemas/4dform/formsSchema.json
```

Use this schema when validating a `.4DForm` file.

Do not modify the schema to make an invalid Form pass validation.

## Validation

When validating a `.4DForm`:

1. Confirm that the file is valid JSON.

2. Validate the file against:

   ```
   schemas/4dform/formsSchema.json
   ```

3. Report any validation errors with their location and relevant property
   information when available.

A successful JSON parse alone must not be reported as successful 4D Form
validation.

Use `boon` for JSON Schema validation. For example:

```
boon schemas/4dform/formsSchema.json <file>
```

Do not assume that `jq` alone performs JSON Schema validation.

## Modification

When modifying a `.4DForm`:

* Preserve the existing JSON structure.
* Make the smallest necessary change.
* Preserve properties that are not directly involved in the requested change.
* Do not remove unknown properties merely because they are not understood.
* Do not arbitrarily reorder properties.
* Avoid unrelated formatting changes.
* Do not introduce properties based solely on assumptions about 4D.

After modification, validate the resulting file against the 4D Form schema.

Review the resulting diff for unintended changes.

## Generic JSON Tools

Generic JSON tools may be used for inspection and syntax validation.

For example:

```
jq empty <file>
```

However, generic JSON validation does not replace 4D Form schema validation.

## Schema Errors

If a Form fails schema validation, determine whether:

* the file is malformed;
* the property/value does not satisfy the schema;
* the wrong version of the schema is being used; or
* the schema does not describe the artifact correctly.

Do not "fix" validation failures by weakening or modifying the schema.

## Tool Dependencies

This skill requires `boon` for JSON Schema validation.

Prefer `tools/4dform/boon` over any system-installed boon. Before validating,
check whether it has been provisioned:

```sh
test -x tools/4dform/boon
```

If `tools/4dform/boon` does not exist, follow the download procedure in
`skills/4dtools/SKILL.md` to provision it.

Use `tools/4dform/boon` (or `tools\4dform\boon.exe` on Windows) in all validation
commands -- do not use a bare `boon`:

```
tools/4dform/boon schemas/4dform/formsSchema.json <file>
```

Do not duplicate tool installation logic in this skill.

## Output

When reporting validation results, identify:

* the file;
* whether JSON syntax validation succeeded;
* whether schema validation succeeded;
* the relevant schema;
* each validation error, including its path/location when available.
