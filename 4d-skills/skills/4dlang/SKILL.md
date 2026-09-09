---
name: 4dlang
description: >
  Look up correct 4D syntax before writing code, across both the classic 4D
  language and the 4D object (OOP) language, via 4d-language-classic and
  4d-language-oop. The two corpora overlap (classic `File` vs OOP `4D.File`),
  so query both and compare rather than picking one language up front.
---

# 4D Language Lookup

## Scope

This skill looks up correct 4D syntax and compiler-verified examples before
writing or fixing code, across **both** 4D language subsets:

* **classic 4D language** (procedural commands, e.g. `ALERT`, `Get document size`)
  via `4d-language-classic`
* **4D object (OOP) language** (classes and their members, e.g.
  `4D.File`, `Collection.orderBy`) via `4d-language-oop`

Both are deterministic, offline lookup tools over a compiler-verified IR --
not language models. The same query always returns the same result on any
machine. Neither substitutes for `validate`/`check-syntax` (see the `4dlsp`
skill) -- always still compile-check the code you write.

## Why one skill, not two

An agent asking "how do I read a text file in 4D" does not know in advance
whether the answer is a classic command or an OOP class member. A skill
that forces that choice up front is unusable for exactly the queries that
matter most. The two corpora also genuinely **overlap**: 4D has a classic
command literally named `File` that constructs and returns a `4D.File`
object --

```
$ tools/4dlang/4d-language-classic query "File" --limit 10 --json | \
  python3 -c "import json,sys; [print(x['id'], x['score']) for x in json.load(sys.stdin) if x['id']=='File']"
File 34.727154
```

-- so "the classic answer" and "the OOP answer" for a file-handling question
are frequently two views of the same feature, not competitors. Query both.

## Tool location

Prefer `tools/4dlang/4d-language-classic` and `tools/4dlang/4d-language-oop`
over any system-installed copy. If either does not exist, provision it first
by reading `skills/4dtools/SKILL.md`.

```sh
test -x tools/4dlang/4d-language-classic
test -x tools/4dlang/4d-language-oop
```

On Windows, check for `tools\4dlang\4d-language-classic.exe` and
`tools\4dlang\4d-language-oop.exe`.

Both tools share the same `query`/`serve` flags (`--limit N`, `--json`,
`--port`), so routing between them needs no special-casing beyond picking
which binary(ies) to invoke.

```sh
tools/4dlang/4d-language-classic query "how do I parse json" --limit 3 --json
tools/4dlang/4d-language-oop     query "sort an entity selection" --limit 3 --json
```

`4d-language-oop` additionally has four OOP-only subcommands with no
classic equivalent:

```
4d-language-oop class <class>                    [--json]
4d-language-oop member <Class.member>            [--json]
4d-language-oop members --class <class> [--kind function|property|constructor] [--json]
4d-language-oop returns <class>                  [--json]
```

A long-running task that will look up many things can instead start each as
an HTTP server once (`serve --port <port>`) and query over HTTP, avoiding
repeated process startup:

```
4d-language-classic serve --port 8080  # GET /lookup, /health
4d-language-oop     serve --port 8081  # GET /lookup, /class, /member, /members, /returns, /health
```

## The routing heuristic: query both, then compare by content

There is no reliable way to tell from the English question alone which
language subset answers it, and the two tools' scores are **not on a
shared scale** -- a higher number from one binary does not mean it beat the
other. Judge by whether the returned summary/example actually addresses the
query, not by comparing raw scores across tools.

**Worked example -- OOP answers, classic does not:**

```
$ tools/4dlang/4d-language-oop query "read a text file line by line" --limit 1
```
returns the `4D.FileHandle` class card (members include `.readLine`,
`.readText`, `.breakModeRead`) -- a direct hit. The same query against
classic:

```
$ tools/4dlang/4d-language-classic query "read a text file line by line" --limit 2
1. DOM Parse XML source ...
2. Load 4D View document ...
```
returns two commands about XML parsing and 4D View documents -- neither is
about reading a text file, and rephrasing the query (`"read line from
document"`, `"read text file"`) surfaces the same kind of irrelevant
results. Line-based text reading in 4D is done through
`4D.FileHandle.readLine`; the answer here is genuinely OOP-only.

**Worked example -- classic answers, OOP does not:**

```
$ tools/4dlang/4d-language-classic query "hash a password" --limit 2
1. Verify password hash ...  score=99.64
2. Generate password hash ...  score=95.60
```
Both are exact, high-confidence hits. The same query against OOP:

```
$ tools/4dlang/4d-language-oop query "hash a password" --limit 1 --json
```
returns the `4D.CryptoKey` class (RSA/EC key generation) at a much lower
score -- a plausible-looking but wrong answer: `4D.CryptoKey` signs and
encrypts, it does not hash passwords. Likewise `create a formula from text`
hits classic's `Formula from string` cleanly, while OOP's best match
(`EntitySelection.orderByFormula`, about sorting) is off-topic. **`hash a
password` and `create a formula from text` have no OOP equivalent** -- a
weak or off-topic OOP result for a classic-only capability is a correct
outcome, not a failed lookup. Do not force an OOP answer where none exists.

**Worked example -- both answer, and both are right:**

```
$ tools/4dlang/4d-language-classic query "get file size" --limit 1
1. Get document size ...  score=49.92
$ tools/4dlang/4d-language-oop query "get file size" --limit 1 --json
class FileHandle / member FileHandle.getSize   score=25.70
```
Both are genuine, correct answers to the same question, in different
language subsets. When this happens, the deciding factor is which language
subset the surrounding code is already written in -- not which tool scored
higher.

## The mixed-array result shape (read this before parsing `query` output)

`4d-language-oop query` returns a **heterogeneous array**. Every element
carries a `resultType` discriminator of `"member"` or `"class"` -- **class
cards appear inline in `query` results**, not only via the `class`
subcommand. This happens whenever many members of one class would
otherwise flood the results (the class-flooding cap is 3 member rows per
class). A consumer that assumes every element is a member record will
mis-render or crash on the class rows. `4d-language-classic query` results
are homogeneous (always commands) -- this discriminator only applies to OOP.

A **class** result (`resultType: "class"`), e.g. from
`4d-language-oop query "order a collection"`:

```json
{
  "resultType": "class",
  "id": "Collection",
  "typeName": "Collection",
  "score": 26.460016,
  "cardReason": "many members of this class matched; showing the class card instead of flooding the results",
  "instantiation": { "recipes": [ /* 3 recipes: literal, New collection, New shared collection */ ] },
  "howToObtain": [ "$c:=[1; 2; 3]   [literal] -- Collection literal — the most idiomatic form.", "/* + 2 more */" ],
  "constructibleByUserCode": true,
  "memberCounts": { "total": 47, "declared": 47, "inherited": 0, "oop_function": 46, "oop_property": 1, "oop_constructor": 0 },
  "members": [ { "id": "Collection.orderBy", "memberName": ".orderBy", "kind": "oop_function", "summary": "Returns a new collection containing all elements of the collection in the specified order" } /* + up to 2 more (class-flooding cap) */ ]
}
```

A **member** result (`resultType: "member"`), e.g. `Collection.multiSort`
from the same query:

```json
{
  "resultType": "member",
  "id": "Collection.multiSort",
  "kind": "oop_function",
  "classId": "Collection",
  "classTypeName": "Collection",
  "receiverKind": "instance",
  "score": 26.460016,
  "rawSyntax": [ "**.multiSort**() : Collection", "**.multiSort**( *colsToSort* : Collection ) : Collection", "**.multiSort**( *formula* : 4D.Function ; *colsToSort* : Collection ) : Collection" ],
  "overloads": [ /* full typed IR overload objects, one per rawSyntax line */ ],
  "example": { "available": true, "primary": { "source": "documentation", "provenance": "documentation example, compiler-verified", "compilerVerified": true, "raw": "..." } }
}
```

Check `resultType` before reading any other field. Do not assume a `query`
response is a flat array of members.

## Instantiation recipes (the highest-value field for code generation)

4D OOP classes are obtained in wildly different ways, and getting this
wrong is the single most common mistake an agent makes writing OOP code.
Every class card carries `instantiation.recipes[]` (raw), `howToObtain`
(rendered one-liners) and `constructibleByUserCode` (boolean). The taxonomy,
verified directly against the vendored IR (`data/vendor/4d-oop-ir.json` in
the `4d-language-oop` checkout):

1. **19 classes have a real `.new()` constructor** -- `Blob`, `CryptoKey`,
   `File`, `Folder`, `HTTPAgent`, `HTTPRequest`, `IMAPNotifier`,
   `IMAPTransporter`, `MailAttachment`, `Method`, `POP3Transporter`,
   `SMTPTransporter`, `SystemWorker`, `TCPConnection`, `TCPListener`,
   `UDPSocket`, `Vector`, `WebSocket`, `WebSocketServer`. E.g.
   `$key:=4D.CryptoKey.new(New object("type"; "RSA"; "size"; 2048))`.
2. **4 abstract base classes** -- `Document`, `Directory`, `Function`,
   `Transporter` -- are never instantiated directly; obtain a concrete
   subclass instead (see "Inherited member resolution and abstract
   classes" below).
3. **4 ORDA templates** -- `cs`, `cs.<DataClass>`, `cs.<DataClass>Entity`,
   `cs.<DataClass>Selection` -- are generated per-project; substitute the
   real dataclass name for `<DataClass>` (`$dataClass:=ds.Employee`).
4. **4 classes cannot be constructed by user code at all** --
   `IncomingMessage`, `TCPEvent`, `UDPEvent`, `WebSocketConnection`.
   Instances arrive only as callback arguments:
   ```
   $ tools/4dlang/4d-language-oop class 4D.IncomingMessage
   4D.IncomingMessage (class IncomingMessage)
   HOW TO OBTAIN AN INSTANCE:
     NOT CONSTRUCTIBLE BY USER CODE.
     Instances of this class are created by 4D and passed into a callback;
     no expression in user code constructs one. Declare the callback
     parameter at this type and use the instance 4D hands you.
     Function handle($request : 4D.IncomingMessage) : 4D.OutgoingMessage
   ```
   Declare a callback parameter at that type (`Function handle($request :
   4D.IncomingMessage) : 4D.OutgoingMessage`) -- do **not** write code that
   tries to construct one, e.g. `4D.IncomingMessage.new()` does not exist.
5. **The remaining 19 of 50 classes** (`4D`, `Class`, `Collection`,
   `DataClass`, `DataStore`, `Email`, `Entity`, `EntitySelection`,
   `FileHandle`, `Formula`, `OutgoingMessage`, `Session`, `Signal`,
   `WebForm`, `WebFormItem`, `WebServer`, `ZipArchive`, `ZipFile`,
   `ZipFolder`) are obtained via a classic command (`$c:=[1; 2; 3]`,
   `$file:=File(...)`) or another object's member
   (`$handle:=File(...).open("write")`).

Always read `howToObtain`/`instantiation` before writing a `New <Class>`-
style constructor call that may not exist for that class.

## The placeholder substitution rule

`example.primary` is always compiler-verified, but when its `source` is
`"synthetic"` it carries a `placeholder_note` and its tokens (`$result1`,
`$options2`, `[SynthTable]`, `cs.SynthOOPHandler`, `SynthOOPCallback`, and
similar) **must be substituted** with the caller's own receiver, values,
and names before the example is usable code. Verified directly from a live
`member --json` call:

```json
"placeholder_note": "Tokens such as $result1/$blobScal2/$options3, [SynthTable], SynthRelated, cs.SynthOOPHandler and SynthOOPCallback in `raw` are auto-generated placeholder variable names, table/dataclass references and stub class names from the check project -- substitute your own receiver expression, variable names, and table/field/class references when adapting this example; do not copy them verbatim."
```

This is a repeat of a **real failure from the classic rollout**: agents
copied the placeholders verbatim into user code. Treat any `synthText`,
`$result`/`$read`/`$receiver`\<N\>, `[SynthTable]`, `SynthRelated`,
`cs.SynthOOPHandler`, or `SynthOOPCallback` token in an example's `raw`
field as a stand-in, never as a literal name to keep. The human-readable
CLI output prints the same warning inline before the code block -- read it
even when not using `--json`.

## Two corpus subtleties

**Multi-variant properties.** Nine properties declare more than one valid
type -- all alternatives are valid simultaneously, none is "the real one":
`Email.bcc`/`.cc`/`.from`/`.to`/`.replyTo`/`.sender` are each `Text |
Object | Collection`; `Document.original` is `4D.File | 4D.Folder`;
`SystemWorker.response` is `Text | Blob`; `WebServer.characterSet` is
`Number | Text`. The CLI labels these `MULTI-VARIANT`:

```
$ tools/4dlang/4d-language-oop member Email.bcc
...
property type: MULTI-VARIANT -- all 3 alternatives are valid: Text | Object | Collection
```

Do not treat the first-listed type as canonical and discard the rest --
`accessorTypes` in JSON is always a list for these.

**Dynamic pseudo-members.** Seven members are name *patterns*, not fixed
names -- `4D.classClassName`, `4D.classStoreName`, `DataClass.attributeName`,
`DataStore.dataclassName`, `Entity.attributeName`,
`EntitySelection.attributeName`, `WebForm.componentName`. They carry no
declared source line, so `rawSyntax` is empty; the CLI falls back to a
`dynamicMember.namePattern` note instead:

```
$ tools/4dlang/4d-language-oop member 4D.classClassName
4D.classClassName (oop_property)
class: 4D (instance member)
summary: Each exposed 4D.Class class in the class store is available as a property of the class store.
DYNAMIC MEMBER: the name is a pattern, not a literal member name.
  pattern: <classClassName>
  names a user or built-in class inside a class store
property type: any
  access: read/write
```

`<classClassName>` is a placeholder for whatever class name actually
appears in the project's class store (e.g. `cs.Invoice`), not a literal
member to write.

## Inherited member resolution and abstract classes

Inherited members are modelled once, on the declaring class. `member
File.exists` resolves to `Document.exists` and reports `requestedAs` /
`inheritedFrom` -- ask for the subclass spelling you actually have, the tool
resolves it:

```
$ tools/4dlang/4d-language-oop member File.exists
Document.exists (oop_property)
class: Document (declared type 4D.Document, instance member)
inherited: File.exists resolves to Document.exists, declared on Document
summary: True if the file exists on disk
```

The four abstract classes (`Document`, `Directory`, `Function`,
`Transporter`) are real, **declarable** 4D types even though instances are
always obtained via a concrete subclass -- `var $x : 4D.Document` compiles
and `tool4d` accepts it:

```
$ tools/4dlang/4d-language-oop class 4D.Document
4D.Document (class Document)
flags: abstract
subclasses: File, ZipFile
HOW TO OBTAIN AN INSTANCE:
  NOT CONSTRUCTIBLE BY USER CODE.
  This is an abstract base class: it is never instantiated directly. Obtain
  an instance of one of its concrete subclasses instead.
note: Document is a real, class-store-resolvable 4D type: tool4d
  check-syntax accepts `var $x : 4D.Document` and rejects fabricated names
  such as `4D.DocumentX` ...
```

`isAbstract` describes **instantiation** guidance only; it says nothing
about whether the type may be named. Do not describe `4D.Document` (or the
other three abstract classes) as unnameable -- declare a variable at that
type when a value may legitimately be either subclass, and construct it via
one of the concrete subclasses (`File`/`ZipFile` for `Document`).

## Workflow

1. Before writing an unfamiliar 4D command or OOP class member, query both
   `4d-language-classic` and `4d-language-oop` (see "The routing heuristic"
   above) rather than assuming which language subset answers the question.
2. Check `resultType` on every OOP result before reading further fields.
3. For a class you intend to instantiate, read `instantiation`/
   `howToObtain`/`constructibleByUserCode` before writing a constructor
   call.
4. Substitute every synthetic placeholder token before using an example as
   real code (see "The placeholder substitution rule").
5. Write the code, then validate it with the `4dlsp` skill -- a lookup
   result alone is not proof the code compiles.

## Windows

Use `tools\4dlang\4d-language-classic.exe` and
`tools\4dlang\4d-language-oop.exe`.
