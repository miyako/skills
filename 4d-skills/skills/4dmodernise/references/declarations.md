# `C_*` → `var` / `#DECLARE`

References:
- Modern variable declarations: https://developer.4d.com/docs/Concepts/variables
- Legacy `C_*` directives (pre-20 R7): https://developer.4d.com/docs/20/Concepts/variables#using-a-c_-directive
- `#DECLARE` for parameters: https://developer.4d.com/docs/Concepts/parameters#declaring-parameters
- Compiler methods: https://developer.4d.com/docs/Project/compiler

Starting with 4D 20 R7, the `C_*` family of declaration commands is
deprecated. Replace them with `var` (local, process and interprocess
variables) and `#DECLARE` (method parameters and return value).

Whether a project is at or above 20 R7 is decided by its
`compatibilityVersion` -- decode and compare it as described in
"4D Version Detection" in `skills/4dproject/SKILL.md`. Do not compare the
raw value as a number (`20A0` is 20 R10).

Token suffixes on any command you touch follow the rules in "Token
Suffixes" in `skills/4dproject/SKILL.md`. `var` and `#DECLARE` are keywords
and never take a token; when you rewrite `C_LONGINT:Cnnn($x)` the old token
simply disappears.

## Scanning

Search all `.4dm` files for lines starting with a `C_` command:

```sh
grep -rnE "^\s*C_(LONGINT|INTEGER|TEXT|STRING|REAL|OBJECT|BOOLEAN|POINTER|BLOB|DATE|TIME|PICTURE|VARIANT|COLLECTION)\b" Project/Sources/
```

They appear in three contexts:

| Context | File location | Example |
|---------|---------------|---------|
| Local variable declarations | Any `.4dm` | `C_LONGINT($x; $y)` |
| Method parameter declarations | Project method `.4dm` | `C_LONGINT($1)`, `C_OBJECT($0)` |
| Compiler variable/method declarations | `Compiler_Variables.4dm`, `Compiler_Methods.4dm` | `C_OBJECT(Address_EN; $0)` |

## Type Mapping

| Legacy command | Modern type | Notes |
|---|---|---|
| `C_LONGINT`, `C_INTEGER` | `Integer` | `Integer` is a long integer |
| `C_REAL` | `Real` | floating point |
| `C_TEXT`, `C_STRING` | `Text` | |
| `C_OBJECT` | `Object` (or a class: `cs.MyClass`, `4D.File`) | |
| `C_COLLECTION` | `Collection` | |
| `C_BOOLEAN` | `Boolean` | |
| `C_POINTER` | `Pointer` | |
| `C_BLOB` | `Blob` | |
| `C_DATE` | `Date` | |
| `C_TIME` | `Time` | |
| `C_PICTURE` | `Picture` | |
| `C_VARIANT` | `Variant` | |

Always give the type explicitly. `var $a:=10` infers `Real`, not
`Integer`.

## Migration Rules

### Rule 1: Local Variables — `C_*` → `var`

**Before:**
```4d
C_LONGINT($x; $y)
C_TEXT($name)
C_OBJECT($options)
```

**After:**
```4d
var $x; $y : Integer
var $name : Text
var $options : Object
```

**Key points:**
- Multiple variables of the same type can share one `var` declaration, separated by semicolons.

### Rule 2: Method Parameters — `C_*($1; $2; ...)` → `#DECLARE`

**Before:**
```4d
C_LONGINT($1)
C_TEXT($2)
```

**After:**
```4d
#DECLARE($param1 : Integer; $param2 : Text)
```

**Key points:**
- `#DECLARE` must be the first non-comment, non-attribute line in the method — this includes coming before **any** executable statement, not just before other declarations. If the original `C_*($N)` line was preceded by executable code (e.g. `SET MENU BAR(1)` before `C_TEXT($1)`), the `#DECLARE` line must be moved above that code when migrating, not simply substituted in place.
- **Numbered parameters (`$1`, `$2`, `$0`) are illegal in `#DECLARE`** — you must assign a named local variable (e.g., `$param1`, `$flag`).
- `#DECLARE` replaces **all** `C_*($N)` declarations for that method.
- For variadic methods, use `#DECLARE(... : Type)` with `Count parameters` and `${N}` notation, or `Copy parameters` to forward arguments to another method.

**⚠️ Common ordering mistake:** Migrating in-place (replacing the `C_*($N)` line with `#DECLARE` at the same line position) is wrong if any executable statement appears earlier in the method. Always re-check the resulting file so that `#DECLARE` (and any `var` lines that follow it) sit directly under the `//%attributes` line, before all other code:

```4d
//%attributes = {}
SET MENU BAR(1)      // ❌ WRONG — executable code before C_* declarations
C_TEXT($1)
```

```4d
//%attributes = {}
#DECLARE($title : Text)  // ✅ CORRECT — #DECLARE moved above the executable code
var $window : Integer

SET MENU BAR(1)
```

### Rule 3: Return Values — `C_*($0)` → `#DECLARE` return syntax

The legacy pattern uses `$0` as a special "return" variable:

**Before:**
```4d
C_OBJECT($result; $0)
$result:=New object
$result.name:="test"
$0:=$result
```

**After:**
```4d
#DECLARE->$result : Object
$result:=New object
$result.name:="test"
```

**Key points:**
- The `->` arrow syntax in `#DECLARE` declares the return variable.
- The named return variable (e.g., `$result`) is automatically returned; no explicit `$0:=` assignment is needed.
- If the method also takes parameters: `#DECLARE($param : Text)->$result : Object`

### Rule 4: Process/Interprocess Variables

Process variables (no `$` prefix) and interprocess variables (`<>` prefix) use the same `var` syntax:

**Before:**
```4d
C_OBJECT(MyProcessVar)
C_LONGINT(<>MyInterprocessVar)
```

**After:**
```4d
var MyProcessVar : Object
var <>MyInterprocessVar : Integer
```

### Rule 5: Compiler Methods Cleanup

4D projects often have `Compiler_Variables.4dm` and `Compiler_Methods.4dm` that pre-declare all process variables and method signatures for the compiler. When migrating:

- **`Compiler_Variables.4dm`**: Convert all `C_*` lines to `var` declarations. This file remains necessary — it declares process-scope variables used across methods.
- **`Compiler_Methods.4dm`**: Remove entries for any method that now uses `#DECLARE`, since `#DECLARE` provides the same type information to the compiler. If all methods use `#DECLARE`, this file can become empty (but keep it with just the attributes line for consistency).

**Before (`Compiler_Methods.4dm`):**
```4d
//%attributes = {"invisible":true}
C_LONGINT(MyMethod; $1)
C_OBJECT(MyMethod; $0)
```

**After (if MyMethod uses `#DECLARE`):**
```4d
//%attributes = {"invisible":true}
  // MyMethod now uses #DECLARE
```

---

## Common Pitfalls

### ❌ Passing non-variables to `C_*` commands

```4d
C_OBJECT($lang; 0)
```

**Why this is wrong:** `C_*` commands accept one or more **variable names** to declare. `0` is an integer literal, not a variable. This was likely a typo for `$0` (the return variable). This is a **syntax error** that may cause unpredictable behaviour depending on the 4D version.

**Detection:** Search for `C_*` calls where any argument is not a valid variable name (i.e., does not start with `$`, `<>`, or a letter).

**Fix:** Identify the intended variable (usually `$0` when found at the end of the argument list), then migrate to `#DECLARE` return syntax.

### ❌ Mixing `#DECLARE` with `C_*` parameter declarations

```4d
#DECLARE($param : Text)
C_LONGINT($1)   // WRONG — conflicts with #DECLARE
```

**Why:** `#DECLARE` replaces all `C_*` parameter declarations. Having both creates a conflict. Remove all `C_*($N)` lines when `#DECLARE` is present.

### ❌ Using numbered parameters in `#DECLARE`

```4d
#DECLARE($1 : Integer)   // WRONG — $1 is illegal in #DECLARE
```

**Why:** `#DECLARE` requires named local variables, not numbered parameters (`$1`, `$2`, `$0`). Numbered parameters are a legacy concept from `C_*` declarations. Use a descriptive name instead:

```4d
#DECLARE($flag : Integer)   // CORRECT
```

For variadic methods where you need numbered access, use the spread syntax:

```4d
#DECLARE(... : Real) : Real
var $i; $total : Real
For ($i; 1; Count parameters)
    $total+=${$i}
End for
return $total
```

Or use `Copy parameters` to forward arguments to another method.

### ❌ Forgetting to remove `$0:=` assignments

```4d
#DECLARE->$result : Object
$result:=New object
$0:=$result   // WRONG — unnecessary and creates a compiler warning
```

**Why:** The `#DECLARE` return variable is automatically returned. Remove the `$0:=` line.

### ❌ Leaving redundant `Compiler_Methods` entries

After adding `#DECLARE` to a method, forgetting to remove the corresponding `C_*(MethodName; $0)` or `C_*(MethodName; $1)` entries from `Compiler_Methods.4dm`. These are now redundant and may cause compiler warnings about duplicate declarations.

### ❌ Using `Integer` where `Real` is needed

`C_LONGINT` maps to `Integer`, but if the variable is used in floating-point arithmetic or assigned decimal values, use `Real` instead. Check the variable's usage context.

Similarly, `C_REAL` used for a variable that only holds whole numbers (e.g., a button value from a form object) should still be typed as `Real` if that is what the form object produces — 4D button values are `Real` by default.

### ❌ Declaring typed arrays with `var`

```4d
var $windows : Array Integer   // WRONG
```

**Why:** In 4D, typed arrays are declared with the `ARRAY ...` commands, not with `var`.

```4d
ARRAY LONGINT($windows; 0)     // CORRECT
```

Use `var` for regular variables and `#DECLARE` for parameters/returns, but keep typed array declarations in the legacy `ARRAY` command family (`ARRAY LONGINT`, `ARRAY TEXT`, `ARRAY OBJECT`, etc.).

### ❌ Re-declaring a variable that is already a form object's `dataSource` — but only if it is *never referenced in method code*

```4d
// Compiler_Variables.4dm
C_REAL(rb1)   // or var rb1 : Real
```

```json
// form.4DForm — rb1 is the dataSource of a radio button
"dataSource": "rb1"
```

**Why this is wrong:** a variable bound as the `dataSource` of a form object (button, radio, input, tab, etc.) *and never referenced anywhere in method code* is auto-typed by the form itself. Declaring it again in `Compiler_Variables.4dm` (via `C_*` or `var`) produces a **"Redefinition of variable"** compiler warning, even though the type matches.

**⚠️ Critical qualifier — this rule does NOT apply once the variable is used in method code.** If the same form-bound variable is also read or assigned inside any `.4dm` method (e.g. `vRow:=1`, `LISTBOX SET ROW HEIGHT(*; "LB0"; vRow; vHeight)`), the compiler cannot infer its type from code alone and will instead report **"The variable X has not been explicitly declared in the typing methods (Compiler...)"** if the declaration is missing. This is the opposite-looking error from the redefinition warning, and it is easy to "fix" the wrong way by removing all form-bound declarations indiscriminately — that was a real regression: a prior pass swept every `Compiler_Variables.4dm` entry that matched a `dataSource` name, which broke compilation for the subset that were also referenced in code.

**Fix — verify both directions before touching `Compiler_Variables.4dm`:**
1. Grep every `form.4DForm` for `"dataSource": "<name>"` to find form-bound variables.
2. For each one, grep all `.4dm` files for uses of that exact name **outside** the form JSON (assignments or reads in method bodies, not just the dataSource binding itself).
3. **Referenced only via `dataSource`, never in code** → remove/omit the explicit declaration; rely on the form binding.
4. **Referenced in method code too** → keep (or restore) an explicit `var Name : Type` declaration in `Compiler_Variables.4dm`. This is not a contradiction of the "form binding types it" rule — the form binding alone is insufficient once code elsewhere needs to resolve the type independently of the form loading.
5. After changing `Compiler_Variables.4dm`, re-run the compiler check (or re-grep) and confirm neither warning appears: no "Redefinition of variable" for the untouched cases, and no "not been explicitly declared" for the ones referenced in code.

### ❌ Leaving a local variable used across `If`/`Else` branches or reused patterns undeclared

```4d
If (Get database localization(Current localization)="ja")
	$json:=JSON Parse(...)   // WRONG — $json never declared with var
Else 
	$json:=JSON Parse(...)
End if 
COLLECTION TO ARRAY($json; ...)
```

**Why:** local variables (`$name`) need an explicit `var $name : Type` just as much as process variables — a local only ever assigned inside conditional branches is easy to miss because it "looks" declared by virtue of being assigned. The compiler reports **"The variable $JSON has not been explicitly declared..."** if this is skipped.

**Fix:** add `var $json : Collection` (or the appropriate type) once, near the top of the method, before any branch that assigns it — the same method-scoped placement rule as any other local.

### ❌ Assigning a scalar to a name that is declared/used elsewhere as an array

```4d
// Compiler_Arrays.4dm
ARRAY TEXT(TabControl; 0)

// initForm.4dm
COLLECTION TO ARRAY($json; TabControl; "Title"; TextTabControl; "Text")
TabControl:=0   // WRONG — collides with the array declaration above
```

**Why:** 4D does not allow a name to be both an array and a scalar. This also produces a **"Redefinition of variable"** warning, but the root cause is a genuine logic bug (leftover code from before the name was repurposed as an array), not a directive-syntax issue — converting `C_*`/`ARRAY` syntax alone will not fix it.

**Fix:** before migrating, grep every assignment site (`<name>:=`) and every declaration site (`ARRAY ...(<name>...)` / `C_*(<name>)`) for the same identifier across the whole project. If a name is used both as a scalar and as an array anywhere, that is a pre-existing bug — resolve the conflicting assignment (usually by deleting dead/leftover code) rather than silently picking one type.

### ❌ Redeclaring the same local variable in multiple branches of one method

```4d
If (Count parameters=0)
	var $window : Integer
	...
Else 
	var $window : Integer   // WRONG — "Redefinition of variable $window"
	...
End if 
```

**Why:** `var` declarations are scoped to the **whole method**, not to the `If`/`Else` block they appear in — unlike block-scoped languages. Declaring the same name in two branches is a redefinition even though the branches are mutually exclusive at runtime.

**Fix:** declare the variable exactly once, before the branching logic that uses it in more than one branch:

```4d
var $window : Integer

If (Count parameters=0)
	...
Else 
	$window:=Open form window(...)
End if 
```

---

## Audit Procedure

1. **Check the project version** (`skills/4dproject/SKILL.md`). At or above
   20 R7, migrate.
2. **Find every `C_*` declaration** with the grep above.
3. **Categorise each occurrence:**

   | Category | Pattern | Action |
   |---|---|---|
   | Local variables | `C_*($varName)` | → `var $varName : Type` |
   | Parameters | `C_*($1)`, `C_*($2)` | → `#DECLARE($name : Type)` |
   | Return value | `C_*($0)` or `C_*(MethodName; $0)` | → `#DECLARE(...)->$name : Type` |
   | Process variables | `C_*(VarName)` (no `$`) | → `var VarName : Type` |
   | Compiler method entries | `C_*(MethodName; $N)` | → remove if the method has `#DECLARE` |

4. **Apply per method:** one `#DECLARE` line for all parameters (+ return),
   moved above all executable code; `var` for locals; delete `$0:=` lines;
   clean `Compiler_Methods.4dm`; convert `Compiler_Variables.4dm`.
5. **Verify** that the grep returns nothing, then validate every changed
   `.4dm` with the `4dlsp` skill. Converting syntax alone is not proof: if a
   compile check is available, confirm no "Redefinition of variable" and no
   "not been explicitly declared" diagnostics remain.

A method that now has required `#DECLARE` parameters cannot run from the
Run Method dialog -- audit its visibility at the same time (`4dmethods`
skill).

## Checklist

- [ ] Project version confirmed at or above 20 R7
- [ ] All `C_*` local declarations replaced with `var`
- [ ] All `C_*($N)` parameter declarations replaced with one `#DECLARE`
- [ ] `#DECLARE` placed above **all** executable statements, not where the old `C_*` line was
- [ ] All `C_*($0)` converted to `#DECLARE->$name : Type`, and every `$0:=` removed
- [ ] `Compiler_Methods.4dm` cleaned of entries for methods now using `#DECLARE`
- [ ] `Compiler_Variables.4dm` converted to `var`, removing declarations **only** for form `dataSource` names never referenced in method code
- [ ] Every local assigned only inside `If`/`Else`/`Case of` branches is declared once, above the branching logic
- [ ] No variable declared with `var` in more than one branch of the same method
- [ ] No name used both as a scalar and as an array anywhere in the project
- [ ] No non-variable arguments left in remaining `C_*` calls (e.g. `0` for `$0`)
- [ ] Types correct (`C_LONGINT` → `Integer`, `C_REAL` → `Real`, `Real` kept where decimals or button values are involved)
- [ ] No mix of `#DECLARE` and `C_*($N)` in one method
- [ ] Typed arrays still declared with `ARRAY ...`, not `var`
- [ ] Every changed `.4dm` validated with `4dlsp`
