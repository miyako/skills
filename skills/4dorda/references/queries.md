# ORDA Query Strings

`$dataclass.query()` and `$entitySelection.query()` take a query string
plus values and an optional `querySettings` object. Rules here apply to
both.

Reference: https://developer.4d.com/docs/API/DataClassClass#query

Some rules adapted from the 4d-depot agent instructions by Mathieu Ferry
(MIT License).

## Shape

```
attributePath comparator value {& | | attributePath comparator value} {order by attributePath {asc | desc}}
```

* The left side is an **attribute path** (`lastName`, `employer.name`,
  `info.city`), not an expression. To filter on a computed value, use a
  formula (below) or a computed attribute with a `query` function
  (`skills/4dorda/SKILL.md`).
* Conjunctions: `and` / `&`, `or` / `|`, `not` / `!`.
* `=` (and `==`) treats `@` as a wildcard and is neither case- nor
  diacritic-sensitive. `===` / `IS` treats `@` as a literal character.
* `IN :1` takes a collection value: `query("status IN :1"; ["open"; "new"])`.
* Booleans in the string are `true` / `false` (lowercase).

## Placeholders

Pass values through placeholders, never by concatenating text into the
query string. Besides avoiding quoting and type errors, this prevents query
injection: a user-typed value is matched as a value, never parsed as
criteria.

```4d
// indexed placeholders: values follow the query string
$sel:=ds.Employee.query("lastName = :1 and salary > :2"; $name; $min)

// named placeholders: values go in querySettings.parameters
$sel:=ds.Employee.query("lastName = :name"; {parameters: {name: $name}})

// attribute-path placeholders: querySettings.attributes
$sel:=ds.Employee.query(":att = :1"; $value; {attributes: {att: $attrName}})
```

Named values are read only from `querySettings.parameters`; a flat object
such as `{name: $name}` is not used as a placeholder source.

## Null Values

| Goal | Write |
|---|---|
| Attribute is null | `query("spouse = null")` -- literal `null`; a placeholder holding Null does not work |
| Attribute is not null | `query("spouse # null")` |
| Different from a value, **including** nulls | `query("status # :1 \| status = null"; "closed")` |

`#` (`!=`) never returns entities whose attribute is null or undefined, so
"everything except X" silently drops the null rows unless the
`| attr = null` branch is added.

## Order By in the Query

An `order by` clause returns a sorted selection in one call:

```4d
$sel:=ds.Employee.query("salary > :1 order by lastName asc, firstName asc"; $min)
```

Several keys are separated by commas; the default direction is ascending.

## Formulas

A formula criterion is evaluated for each entity (`This` is the entity) and
must return a Boolean. It is sequential, so combine it with indexed criteria
when possible.

```4d
$sel:=ds.Employee.query("eval(Length(This.lastName) >= 30)")

var $settings:={args: {exclude: "-"}}
$sel:=ds.Employee.query("eval(checkName($1.exclude))"; $settings)  // args arrive as $1
```

* Text formulas must be wrapped in `eval()`; a Formula object can be passed
  as a placeholder value instead.
* Inside a formula only `&` and `|` are logical operators.
* When the query string comes from a user, pass `{allowFormulas: False}` in
  `querySettings` so that an `eval()` in the input raises an error instead
  of running code.

## Collections in Object Attributes

| Need | Write |
|---|---|
| One element matches several criteria | `query("places.locations[a].kind = :1 and places.locations[a].city = :2"; "home"; "paris")` |
| At least one element differs | `query("info.coll[a].val # :1"; 0)` |

Without a letter, criteria on `coll[]` may be met by **different**
elements, and `coll[].val # x` matches only when **all** elements differ.
Use one letter per linked group (up to 26 groups per query).

## Vector Similarity (4D 21+)

For an attribute storing `4D.Vector` objects (catalog:
`skills/4dcatalog/SKILL.md`), the value is a comparison object:

```4d
var $cmp:={vector: $vector; metric: mk cosine; threshold: 0.7}
$sel:=ds.Document.query("embedding > :1 order by embedding desc"; $cmp)
// $sel.first() is the most similar
```

| Property | Meaning |
|---|---|
| `vector` | Mandatory `4D.Vector` |
| `metric` | `mk cosine` (default), `mk dot`, `mk euclidean` |
| `threshold` | Default `0.5`; compared with `<`, `<=`, `>`, `>=` only |

* cosine / dot: higher = more similar → `> :1` and `order by ... desc`.
* euclidean: lower = more similar → `< :1` and ascending order.
* Only one vector attribute can drive `order by`; if the same attribute
  appears twice, the first comparison is used for ordering.
* Vectors usually come from an embeddings model, e.g. through 4D AI Kit
  (`skills/4daikit/SKILL.md`).
