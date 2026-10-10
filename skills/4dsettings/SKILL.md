---
name: 4dsettings
description: >
  Work with 4D settings files (.4DSettings). This skill is currently a
  placeholder; settings-specific schema and validation rules have not yet
  been added.
---

# 4D Settings

## Scope

This skill covers 4D settings files:

* `*.4DSettings`

## Status

**Stub — validation support not yet implemented.**

No 4DSettings schema or settings-specific validator is currently available
in this skillset.

## Current Guidance

When working with a `.4DSettings` file:

* Treat it as a 4D-specific artifact, not merely as generic XML.
* Preserve existing structure and elements.
* Make the smallest necessary changes.
* Do not remove unknown elements or attributes.
* Do not assume that well-formed XML implies valid 4DSettings.
* Do not invent schema rules or settings-specific semantics.
* Do not modify the schema collection to make a file pass validation.

Generic XML well-formedness can be checked with an appropriate XML tool when
useful, but this does **not** constitute 4DSettings validation.

## Future

This skill will be expanded when a 4DSettings schema and/or
4DSettings-specific validation rules become available.
