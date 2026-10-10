---
name: 4dorda
description: >
  Write 4D ORDA code: ds dataclasses, entities and entity selections,
  query() strings with indexed and named placeholders, null queries, the #
  comparator and null values, order by inside the query, formula queries
  and allowFormulas, linked collection criteria, vector similarity queries,
  relation traversal, null-safe use of attribute values, save() status,
  optimistic locking with dk auto merge, lock()/unlock(), bulk import with
  fromCollection(), and computed attributes in entity classes. Use when
  writing or reviewing .4dm code that reads or writes data through ds.
---

# 4D ORDA

## Scope

Data access through ORDA in `.4dm` code:

* dataclasses (`ds.Employee`), entities (`cs.EmployeeEntity`) and entity
  selections (`cs.EmployeeSelection`)
* `query()` syntax, placeholders, null handling, formulas, vector
  similarity -- `references/queries.md`
* creating, saving, dropping and locking entities
* bulk import with `fromCollection()`
* computed attributes in `<Dataclass>Entity.4dm` classes

### Not in this skill

| Topic | Skill |
|---|---|
| Tables, fields, relation names, indexes in `catalog.4DCatalog` | `4dcatalog` |
| Exact signature of a class member (`EntitySelection.orderBy`, ...) | `4dlang` |
| Language pitfalls (precedence, `Formula` and `This`, Null vs undefined) | `4dlang` (`references/pitfalls.md`) |
| Per-language attributes (`nameEN` / `nameJA` → computed `name`) | `4dlocalise` (`references/language-attributes.md`) |
| Binding entity selections to list boxes | `4dform` (`references/objects/listbox.md`) |
| Validating `.4dm` | `4dlsp` |

## Route Table

| Task involves | Open |
|---|---|
| Query strings, placeholders, null, `#`, `order by`, formulas, collections, vectors | `references/queries.md` |
| Entities, saving, locking, null safety, `fromCollection`, entity classes | this file |

References:
- ORDA overview: https://developer.4d.com/docs/ORDA/overview
- Entities and selections: https://developer.4d.com/docs/ORDA/entities
- Data model classes: https://developer.4d.com/docs/ORDA/ordaClasses
- `DataClass` class: https://developer.4d.com/docs/API/DataClassClass
- `Entity` class: https://developer.4d.com/docs/API/EntityClass
- `EntitySelection` class: https://developer.4d.com/docs/API/EntitySelectionClass

Some rules adapted from the 4d-depot agent instructions by Mathieu Ferry
(MIT License).

## Basics

```4d
var $all : cs.EmployeeSelection:=ds.Employee.all()
var $one : cs.EmployeeEntity:=ds.Employee.get($id)  // Null if not found

var $new : cs.EmployeeEntity:=ds.Employee.new()
$new.lastName:="Smith"
var $status : Object:=$new.save()
```

* Dataclass, attribute and relation names come from the catalog and are
  case-sensitive in code (`ds.Employee.lastName`).
* A table is visible to ORDA only if it has a single-field primary key
  (`skills/4dcatalog/SKILL.md`).
* Navigate relations instead of querying foreign keys:
  `$employee.employer` (N→1, an entity or Null) and `$company.employees`
  (1→N, an entity selection) rather than
  `ds.Employee.query("companyID = :1"; ...)`.
* `$sel[$i]` is **not assignable**: it cannot be used directly with
  `.save()`, `.lock()` or attribute assignment. Copy it to a variable
  first:

  ```4d
  var $e : cs.EmployeeEntity:=$sel[0]
  $e.lastName:="Smith"
  $e.save()
  ```

* `.extract("name")` returns flat values (`["a"; "b"]`) -- the shape a
  drop-down `values` collection needs. `.toCollection("name")` returns
  objects (`[{name: "a"}; ...]`).

## Null Safety

An attribute that was never set is **Null** unless the field has
`never_null="true"` ("Map NULL values to blank values", see
`skills/4dcatalog/SKILL.md`). Reading a property of Null, concatenating
Null with `+`, or comparing it with `<` / `>` raises a runtime error
(observed as error 15, incompatible operands).

```4d
// fails when birthDate is Null
$label:="Born "+String($e.birthDate)

// safe
$label:=($e.birthDate#Null) ? ("Born "+String($e.birthDate)) : ""
```

Test `#Null` before using an attribute value in an expression, or set
`never_null` on the field when blank values are acceptable. The same
applies to N→1 relations: `$e.employer` is Null when the link is empty.

## Saving and Dropping

`.save()`, `.drop()` and `.lock()` return a status object; locking and stamp
conflicts are **not** thrown. Always check `success`:

```4d
var $status : Object:=$e.save()
If (Not($status.success))
	// $status.status is a dk status ... constant, $status.statusText a label
End if
```

* **Optimistic locking** (default): `save()` fails with
  `dk status stamp has changed` when another process saved the entity after
  it was loaded.
* `$e.save(dk auto merge)` merges concurrent changes made to **different**
  attributes; it fails with `dk status automerge failed` when both changed
  the same attribute. `$status.autoMerged` tells whether a merge happened.
* **Pessimistic locking:** `$e.lock()` fails with `dk status locked` when
  another process holds the lock. Call `.unlock()` as many times as
  `.lock()`; a lock is also released when no reference to the entity remains
  in memory.

## Bulk Import -- `fromCollection()`

`ds.<Dataclass>.fromCollection($objects)` creates or updates one entity per
object and returns the entity selection. It does not return a status:
wrap it in `Try` / `Catch`.

* Property names must equal attribute names **exactly** (case included).
  Unknown properties are ignored; a property whose type does not match the
  attribute is not filled; a missing property leaves the attribute Null --
  which then fails on a `not_null` field.
* Primary key omitted → entity created, key generated. Key given and
  existing → entity updated. `__NEW: true` forces creation and errors if the
  key exists.
* Link a related entity in the same pass with a nested object holding its
  key: `{lastName: "Smith"; employer: {__KEY: 121}}`. The related entity
  itself is not created or updated this way.
* When related keys are not known in advance (auto-generated), import in
  two passes: create parents and children, then link each child to its
  parent through a helper property of the source objects (e.g.
  `departmentName`) and save.
* Iterate parsed JSON with `Object` variables, not
  `cs.<Dataclass>Entity`: helper properties do not exist on entities.

```4d
var $data : Collection:=JSON Parse(File("/RESOURCES/employees.json").getText())
If (ds.Employee.all().length=0)
	Try
		ds.Employee.fromCollection($data)
	Catch
		// Last errors
	End try
End if
```

## Entity Classes and Computed Attributes

`Project/Sources/Classes/<Dataclass>Entity.4dm`:

```4d
Class extends Entity

Function get fullName() : Text
	return String(This.firstName)+" "+String(This.lastName)
```

* `Class extends Entity` (or `EntitySelection`, `DataClass`, `DataStore`)
  must match the parent class name exactly (case-sensitive).
* A computed attribute is read like a stored one, including in forms
  (`Form.employee.fullName`). In `query()` and `orderBy()` it works but is
  evaluated sequentially unless the class also implements
  `Function query fullName($event : Object)` /
  `Function orderBy fullName($event : Object)` mapped to stored, indexed
  attributes.
* Make getters Null-safe: they run for every displayed row.

## Checklist

- [ ] Query values passed through placeholders, never concatenated (`references/queries.md`)
- [ ] Null searched with the literal `null`, not a placeholder
- [ ] `save()` / `drop()` / `lock()` status checked
- [ ] Attribute values tested `#Null` before string or arithmetic use
- [ ] `$sel[$i]` copied to a variable before modifying or saving
- [ ] `fromCollection()` property names match attribute names exactly
- [ ] Changed `.4dm` validated with `4dlsp`
