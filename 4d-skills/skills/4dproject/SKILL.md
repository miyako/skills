---
name: 4dproject
description: >
  Work with 4D project definition files (.4DProject). This skill is currently
  a placeholder; project-specific schema and validation rules have not yet
  been added.
---

# 4D Project

## Scope

This skill covers 4D project definition files:

* `*.4DProject`

## Status

**Stub — validation support not yet implemented.**

No 4DProject schema or project-specific validator is currently available
in this skillset.

## Current Guidance

When working with a `.4DProject` file:

* Treat it as a 4D-specific artifact, not merely as generic JSON.
* Preserve existing structure and properties.
* Make the smallest necessary changes.
* Do not remove unknown properties or fields.
* Do not assume that valid JSON implies a valid 4DProject.
* Do not invent schema rules or project-specific properties.
* Do not modify the schema collection to make a file pass validation.

Generic JSON syntax can be checked with an appropriate JSON tool when useful,
but this does **not** constitute 4DProject validation.

## Future

This skill will be expanded when a 4DProject schema and/or
4DProject-specific validation rules become available.
