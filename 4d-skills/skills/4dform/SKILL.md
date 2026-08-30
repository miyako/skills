---
name: 4dform
description: >
  Work with 4D Form source files (.4DForm), including understanding,
  modifying, and validating their JSON structure against the 4D Form schema.
---

# 4D Form

## Scope

This skill covers 4D Form source files:

* `*.4DForm`

A `.4DForm` file is a 4D-specific JSON artifact.

Do not treat a `.4DForm` as generic JSON. Generic JSON validity is necessary
but is not sufficient to establish that the artifact is a valid 4D Form.

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

Prefer `tools/boon` over any system-installed boon. Before validating,
check whether it has been provisioned:

```sh
test -x tools/boon
```

If `tools/boon` does not exist, follow the download procedure in
`skills/4dtools/SKILL.md` to provision it.

Use `tools/boon` (or `tools\boon.exe` on Windows) in all validation
commands -- do not use a bare `boon`:

```
tools/boon schemas/4dform/formsSchema.json <file>
```

Do not duplicate tool installation logic in this skill.

## Output

When reporting validation results, identify:

* the file;
* whether JSON syntax validation succeeded;
* whether schema validation succeeded;
* the relevant schema;
* each validation error, including its path/location when available.
