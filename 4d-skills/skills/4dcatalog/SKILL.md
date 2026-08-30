---
name: 4dcatalog
description: >
  Work with 4D Catalog source files (.4DCatalog), including understanding,
  modifying, and validating their XML structure against the 4D Catalog DTD.
---

# 4D Catalog

## Scope

This skill covers 4D Catalog source files:

* `*.4DCatalog`

A `.4DCatalog` file is a 4D-specific XML artifact.

Do not treat a `.4DCatalog` as generic XML. XML well-formedness is necessary
but is not sufficient to establish that the artifact is a valid 4D Catalog.

## Schema

The 4D Catalog DTD is:

```
schemas/4dcatalog/base_core.dtd
```

Use this DTD when validating a `.4DCatalog` file.

Do not modify the DTD to make an invalid Catalog pass validation.

## Validation

When validating a `.4DCatalog`:

1. Confirm that the file is well-formed XML.

2. Validate the document against:

   ```
   schemas/4dcatalog/base_core.dtd
   ```

3. Report validation errors with their location and relevant element or
   attribute information when available.

A successful XML parse alone must not be reported as successful 4D Catalog
validation.

Use an XML validator capable of DTD validation.

For example, where `xmllint` is available:

```
xmllint --noout --dtdvalid schemas/4dcatalog/base_core.dtd <file>
```

If the Catalog's DTD declaration or validation mechanism requires a
different invocation, follow the structure of the actual artifact rather
than modifying the document merely to accommodate the command.

## Modification

When modifying a `.4DCatalog`:

* Preserve the existing XML structure.
* Make the smallest necessary change.
* Preserve elements and attributes that are not directly involved in the
  requested change.
* Do not remove unknown elements or attributes merely because they are not
  understood.
* Preserve the existing document encoding and XML declaration where
  practical.
* Avoid unrelated formatting or whitespace changes.
* Do not introduce elements or attributes based solely on assumptions about
  4D.

After modification, validate the resulting file against the 4D Catalog DTD.

Review the resulting diff for unintended changes.

## Generic XML Tools

Generic XML tools may be used for inspection and well-formedness checks.

For example:

```
xmllint --noout <file>
```

However, well-formed XML does not replace validation against the 4D Catalog
DTD.

XPath may be used for targeted inspection when useful.

## DTD Errors

If a Catalog fails DTD validation, determine whether:

* the XML is malformed;
* an element is missing or unexpected;
* an attribute is invalid or missing;
* the document references the wrong DTD;
* the applicable 4D version uses a different structure; or
* the supplied DTD does not completely describe the artifact.

Do not "fix" validation failures by weakening or modifying the DTD.

## Tool Dependencies

If `xmllint` or another required validation tool is unavailable, use the
`4dtools` skill to provision the required tool when applicable.

Do not duplicate tool installation logic in this skill.

## Output

When reporting validation results, identify:

* the file;
* whether XML well-formedness validation succeeded;
* whether DTD validation succeeded;
* the DTD used;
* each validation error, including its location when available.
