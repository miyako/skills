# Data That Follows the UI Language

When a dataclass stores one attribute per language (`nameEN`, `nameFR`,
`nameJA`, ...), add a **computed attribute** to the entity class so forms,
list boxes, sorts and code can use one name (`name`) that follows the
current UI language.

References:
- Computed attributes: https://developer.4d.com/docs/ORDA/ordaClasses#computed-attributes-1
- `Get database localization`: https://developer.4d.com/docs/commands/get-database-localization

`Project/Sources/Classes/<Dataclass>Entity.4dm`:

```4d
Class extends Entity

Function get name() : Text
	var $lang : Text
	$lang:=Get database localization(Current localization)
	Case of
		: ($lang="ja")
			return This.nameJA
		Else
			return This.nameEN
	End case

Function orderBy name($event : Object) : Text
	var $lang : Text
	$lang:=Get database localization(Current localization)
	Case of
		: ($lang="ja")
			return "nameJA "+$event.operator
		Else
			return "nameEN "+$event.operator
	End case
```

* **Always add `orderBy`.** Without it, sorting on `name` runs the getter on
  every entity (sequential sort); with it, the sort runs on the stored,
  indexed attribute.
* **Querying** a computed attribute needs a `query` function too. Without
  one, keep queries on the stored attributes (`query("nameJA = :1"; ...)`).
* If the dataclass already has a stored `name` attribute, ask the user
  before introducing a computed one.
* Then replace `nameEN` (and similar) with `name` in list box columns, sorts
  and display code where the UI should follow the language.
* Adding a new language attribute (e.g. `nameJA`) changes the catalog -- see
  the `4dcatalog` skill -- and usually the data import code.

## Verifying

With 4D or tool4d (`4dcli` skill), run a test method that, for each
language (`SET DATABASE LOCALIZATION`):

* compares the primary keys returned by `ds.City.all().orderBy("name asc")`
  with those of `orderBy("nameJA asc")` (and `desc`);
* to prove the `orderBy` function is really called, make it temporarily
  return something different (e.g. `"ID desc"`) in a throw-away copy of the
  project, never in the repository.
