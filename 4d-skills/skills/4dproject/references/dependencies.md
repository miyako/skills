# Installing a component dependency in a host project

Read `references/component-releases.md` first when the question is *which
version or tag to publish*. This reference is the consumer side: a host
project that wants to call a component's classes.

## Declaring the dependency

`Project/Sources/dependencies.json` is the project's dependency declaration:

```json
{
  "version": 2100,
  "dependencies": {
    "DateTime": {
      "github": "miyako/DateTime",
      "tag": "0.1.3"
    }
  }
}
```

The key (`DateTime`) is the component name; 4D's Dependency manager
resolves `github` + `tag` to that repository's release asset
(`<repository>.zip`) and installs the unpacked `.4dbase`. Pin a `tag`;
floating branches make a build non-reproducible. `{"DateTime": {}}` is the
local form used when the component folder is provided beside the project.

Only the full 4D application (IDE) acts on this file. `tool4d` does not —
see "Headless tool4d" below.

## Where a local component is picked up

| Location | Notes |
|---|---|
| `<project>/Components/<Name>.4dbase` | Highest priority; the folder 4D and `tool4d` load at startup. Use this for a component copied by hand or by a script. |
| `<project>/<Name>.4dbase` (beside `Project/`) | Resolved by the Dependency manager as a local dependency; **not** loaded by `tool4d`. |

A component package is a folder whose name ends in `.4dbase`:

* **compiled**: the `.4DZ` file, `Resources/` and native `Libraries/`
  (what a release ZIP contains);
* **source**: a `Project/` folder with the component's `.4dm` sources.

An interpreted host can use either; a compiled host requires a compiled
component. Do not edit files inside a downloaded component: it is a
dependency, and its revision is the release tag.

Host code reaches the component through the component's declared class
store, `cs.<ComponentName>.<Class>`. Inside the component the same class is
`cs.<Class>`; the namespace exists only in the host.

## Headless tool4d

`tool4d` has no Dependency manager. With a declared dependency it logs:

```
PackageManager No component to fetch dependencies ()
PackageManager Dependency 'DateTime' cannot be found ()
```

and then the dependency is simply absent: `cs.DateTime` is `Null` at
runtime and calls fail with an “Object or Collection Expected” error.
Installing and staging the component yourself is required:

1. Download the release asset (`<repository>.zip`) from the GitHub
   release API for the pinned tag and unpack it under `Components/`.
2. Verify `Components/<Name>.4dbase/<Name>.4DZ` (compiled) or the
   `Project/` folder (source) exists before running.
3. Keep `Components/` out of version control; it is a fetched artifact.
   Regenerate it from the pinned tag instead of committing a binary.

A short Python stand-in for the download is enough — resolve
`https://api.github.com/repos/<owner>/<repo>/releases/tags/<tag>`, pick the
asset whose name is `<repo>.zip`, and reject archive members that escape
the destination directory. Do not duplicate the Dependency manager's
prerelease selection rules; ask for the exact tag.

Observed locally with the DateTime 0.1.3 release: `Components/` staging
works for **interpreted** runs and for `tool4d --startup-method=<method>
--user-param=<json>`, and the component's CLI executes normally.

## Compile-time limit: the class store is not resolved under tool4d

`Compile project` in a `tool4d` session does **not** see a dependency
component's class store. Compiling a host that calls
`cs.DateTime.DateTime.new(...)` produced, on 21.2 LTS (builds 21.100691
and 21.100694) and 21 R5 (21R5.100176):

```
error: The class cs.DateTime is unknown.
warning: The function or property convert does not exist on type cs.DateTime.DateTime. (550.2)
```

The same result appears with the compiled release staged in
`Components/`, with the component's source project staged there, with the
component at the project root, and when `Compile project` is called from a
separate helper project with the component staged in both. The release's
generated `Resources/en.lproj/syntaxEN.json` lists only `new()` for
`cs.DateTime.DateTime`, so the compiler never learns the method
signatures; the class-store error follows from the same missing metadata.

Practical consequences for a **host** project (not a component project):

* Treat an interpreted run against the real component as the acceptance
  evidence for headless CI. Do not promise a compiled-mode check there.
* Keep host code typed as `cs.<ComponentName>.<Class>`: that is the API
  the IDE compiles against once the Dependency manager has installed the
  dependency.
* Compile in the 4D IDE, where the Dependencies panel performs the
  install. This reference has not verified that IDE compile path on a
  clean machine; say so in evidence instead of inferring it from a
  successful interpreted run.
* This is about hosts of a dependency. Compiling a component's own
  matrix project has no such class-store dependency.

## Minimum host wiring checklist

* `Project/Sources/dependencies.json` pins the tag.
* `Components/<Name>.4dbase` exists before any headless run.
* The component's version is visible in the UI or a test report
  (`version()`), so a stale staging is detectable.
* One interpreted acceptance run exercises a success case, a rejection
  (`ok:false` with an error code) and a batch call with a mixed result.
