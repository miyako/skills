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
      "version": "0.1.3"
    }
  }
}
```

The key (`DateTime`) is the component name; 4D's Dependency manager
resolves `github` + `version` to that repository's release asset
(`<repository>.zip`) and installs the unpacked `.4dbase`. Pin an exact
version; floating branches make a build non-reproducible. Declare no version
at all (`{"DateTime": {}}`) only for the local form, where the component
folder is provided beside the project.

**The pin key is `version`, not `tag`.** Declarations written by the IDE on
4D 21 R5 use `"version"`, with `"latest"` and `"4d"` as the two non-numeric
values:

```json
{"dependencies": {"dashboard": {"github": "miyako/dashboard", "version": "latest"}}}
{"dependencies": {"4D AIKit": {"github": "4d/4D-AIKit", "version": "4d"}}}
```

`"4d"` is how the IDE records a component published in 4D's own catalogue
rather than on GitHub. The lock file the IDE maintains
(`userPreferences.<user>/dependencies-lock.json`) echoes the same key back --
`github`, `version`, `loaded`, `found`, `path` for each declared component --
so it is also a way to confirm which key a given build reads.

A wrong key is not diagnosed. The file parses, the dependency stays
declared, and nothing resolves -- which looks like a network or permission
problem. When hand-writing the declaration, compare it against one the IDE
itself wrote. Not observed here: whether the manager also accepts `"tag"` as
an alias; the runs behind this note never resolved through the manager.

Only the full 4D application (IDE) acts on this file. `tool4d` does not —
see "Headless tool4d" below.

## Where a local component is picked up

| Location | Notes |
|---|---|
| `<project>/Components/<Name>.4dbase` | Highest priority; the folder 4D and `tool4d` load at startup. `<project>` is the folder that contains `Project/`: `…/host/Components/CardDAV.4dbase`, **not** `…/host/Project/Components/`. Use this for a component copied by hand or by a script. |
| `<project>/<Name>.4dbase` (beside `Project/`) | Resolved by the Dependency manager as a local dependency; **not** loaded by `tool4d`. |

A component package is a folder whose name ends in `.4dbase`:

* **compiled**: the `.4DZ` file, `Resources/` and native `Libraries/`
  (what a release ZIP contains);
* **source**: a `Project/` folder with the component's `.4dm` sources.

An interpreted host can use either; a compiled host requires a compiled
component. Do not edit files inside a downloaded component: it is a
dependency, and its revision is the release tag.

Staging one level too deep -- `<project>/Project/Components/<Name>.4dbase` --
is silently ignored: the folder is read, never loaded. `tool4d` prints the
usual pair `PackageManager Dependency '<Name>' cannot be found ()` and the
first `cs.<ComponentName>...` call then fails with
`4DRT [-10716] Object or Collection Expected.` because the class store is
`Null`. Observed with CardDAV 0.1.2 on macOS 27.2.1 arm64 / 4D 21.2 LTS
(21.100694); moving the same files up one level fixed the run immediately.

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

Restore the archive's unix mode bits as well. `zipfile` writes every member
as 0644, so a component whose CLI ships as a regular executable loses its
exec bit; each call that spawns it then fails with
`tool4d.POSX [13] Permission denied` and `launch_failed` in the envelope,
which reads like a component bug rather than an unpacking one:

```python
mode = (member.external_attr >> 16) & 0o777
if mode:
    target.chmod(mode)
```

The same rule applies to any tool the skills provision from a ZIP.

Observed locally with the DateTime 0.1.3 release: `Components/` staging
works for **interpreted** runs and for `tool4d --startup-method=<method>
--user-param=<json>`, and the component's CLI executes normally.

The lock file is not the evidence. `userPreferences.<user>/dependencies-lock.json`
is written on every run and recorded `"loaded": false, "found": false,
"path": ""` for a `tool4d` run in which the hand-staged `Components/` copy
loaded and the component's `version()` returned `0.1.2`. `tool4d` has no
Dependency manager, so the lock answers a question nobody asked; read the
component's own `version()` instead.

`Components/` is not the only place `tool4d` will find it. `tool4d` also has a
dependency cache, parallel to the IDE's under the same `Caches` root; priming it
from a project the IDE has already resolved avoids fetching anything and keeps
the project folder clean:

```sh
cp -R ~/Library/Caches/4D/Dependencies/.github/<owner>/<repo>/<tag> \
      ~/Library/Caches/tool4d/Dependencies/.github/<owner>/<repo>/<tag>
cp    ~/Library/Caches/4D/Dependencies/.github/<owner>/<repo>/<tag>.json \
      ~/Library/Caches/tool4d/Dependencies/.github/<owner>/<repo>/<tag>.json
```

Copy the `<tag>.json` with the folder; alone it leaves the tag unresolved. The
`PackageManager ... cannot be found` pair still prints either way. See
[`component-releases.md`](component-releases.md#where-tool4d-looks-for-a-downloaded-dependency)
for the observed before/after.

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
