# Component release versions and tags

## Scope and ownership

Use this reference for 4D **component** distribution through the Dependency
manager. A CLI-backed 4D component is still a component, not a native 4D
plug-in. Do not assume component dependency rules describe native plug-in
distribution.

The [CLI component template's AGENTS.md](https://github.com/miyako/4d-component-template/blob/main/AGENTS.md)
and [4d-cli-component skill](https://github.com/miyako/4d-component-template/blob/main/.github/skills/4d-cli-component/SKILL.md)
own that template's packaging, version synchronization and publication
workflow. Read the destination repository's instructions and scripts too.
This shared reference defines the tag convention, not permission to publish.

## Default component convention: prefix-free major.minor.patch

For this user's component distribution convention, a new release Git tag
**must be exactly `major.minor.patch` (`x.y.z`), e.g. `0.1.0`, never
`v0.1.0` or `vX.Y.Z`**. All three fields are non-negative decimal integers
without leading zeroes. Do not omit a field, add a prefix, or append
prerelease/build labels to these distribution tags.

Use [SemVer](https://semver.org/spec/v2.0.0.html) for the component's own API
version and major/minor/patch increments. SemVer itself allows prerelease
and build labels; the plain three-number distribution tag is this user's
stricter convention for Dependency manager compatibility.

Keep the following surfaces distinct:

| Surface | Meaning / default component example |
|---|---|
| Component version | Its own API/package version, e.g. `0.1.0`, not the 4D engine version |
| Package version metadata | Version fields in manifests, CLI/class metadata and contracts; synchronize the destination's declared component version surfaces |
| Git release tag | Exact ref pointing to the accepted source commit: `0.1.0`; also use that exact string in tag inputs, release URLs and workflow matching |
| GitHub release title | Human-readable label, e.g. `MyComponent 0.1.0 preview`; it does not change the tag |
| GitHub prerelease flag | Release status (`--prerelease`), independent of the tag syntax |
| Release asset | For GitHub Dependency manager installation, `<repository>.zip`, not a versioned archive name |

For an ordinary preview, retain the tag `0.1.0` and mark the GitHub release
as a prerelease; do not turn the tag into `v0.1.0`, `0.1.0-preview` or
`0.1.0+build`. Preview status does not establish that the Dependency manager
will select it: check the consumer's selection rule and prerelease settings.
A later release with changed contents needs a new version/tag; do not move
an existing tag or overwrite its assets.

When adapting release tooling, align tag validators, generators, workflow
filters, packaging inputs, examples and tests. Do not blindly strip `v` from
upstream dependency tags, unrelated tool releases or historical URLs.
Legacy `vX.Y.Z` stable tags may be considered alongside bare stable tags
when calculating the highest numeric version baseline to avoid downgrades;
that does not permit emitting prefixed tags or rewriting published history.

## "Follow 4D version" is a different rule

The [4D article: Follow 4D version](https://blog.4d.com/follow-4d-version-a-smarter-way-to-manage-your-dependencies/)
requires tags aligned with the **4D engine release**, not arbitrary
component SemVer:

| Engine release train | Required tag pattern in the article | Example |
|---|---|---|
| LTS | `x.y.p`: `x` = 4D major, `y` = 4D minor, `p` = component patch/update | `20.2.3` for 4D 20.2 |
| R release | `xRy.p`: `xRy` = 4D R-release, `p` = patch/update | `20R3.2` for 4D 20 R3 |

Neither pattern has a leading `v`. The R-release form is **not SemVer**.
The [current component documentation](https://developer.4d.com/docs/Project/components#naming-conventions-for-4d-version-tags)
also describes these engine-aligned forms and allows the patch part to be
optional; the article's explicit patch forms above avoid that ambiguity.

The article explicitly permits keeping a custom component version in the
**release title**, but says the **tag must strictly match** the selected
rule. A title such as `MyComponent 0.1.0` cannot make tag `0.1.0` follow
4D 20.2 or 20 R3. Conversely, an engine-aligned tag does not require
renaming the component's own API version or package metadata to match it.

Do not advertise an arbitrary `0.1.0` component tag as compatible with
**Follow 4D version**. Ordinary component version selection and engine-aligned
selection are different policies. Before switching policies, explicitly
align the destination's validators, version-to-tag mapping, workflows and
consumer configuration; SemVer-only publishing tooling does not support
R-release tags merely because this reference documents them.

The article documents the strict formats for **Follow 4D version**; it does
**not** establish that every other dependency rule rejects every prefixed
tag. The broader no-leading-`v` rule above is the user's component convention,
not a claim about all 4D dependency resolution.

## Before an authorized publication

Confirm the selected policy, exact package version, exact tag, title and
prerelease flag separately. Verify the tag targets the accepted build's
commit, metadata is synchronized, and the final ZIP follows the
[GitHub component packaging requirements](https://developer.4d.com/docs/Project/components#configuring-a-github-repository).
Follow the destination's build/test/publication gates. Do not create, push,
delete or move tags, or publish releases, without authorization.

Confirm that every change the release is meant to contain is on the branch
being tagged. A pull request shown as merged may have merged into a branch
other than the default one: a pull request opened on top of another
pull request's branch keeps that branch as its base unless it is retargeted,
and merging the first does not move the second. Check the content, not the
status, for example `git branch -r --contains <commit>` or
`git grep <symbol> origin/<default-branch>`.

## Consuming a component from a project

`Project/Sources/dependencies.json` is how a host project declares components.
It must exist **before the first headless open**: without it, 4D may show a
modal "import components" dialog that blocks `--startup-method` runs
indefinitely. A project with no components still needs the file:
`{"version":2100,"dependencies":{}}`.

```json
{
	"version": 2100,
	"dependencies": {
		"Overlay": {
			"github": "miyako/Overlay",
			"version": "0.1.1"
		},
		"LocalThing": {}
	}
}
```

| Entry form | Meaning |
|---|---|
| `"NAME": {}` | References a component; the path comes from the project's `Components/` folder or an `environment4d.json` entry |
| `"NAME": {"github": "owner/repo"}` | Fetched from GitHub |
| `"NAME": {"gitlab": "owner/repo"}` | Fetched from gitlab.com; add `"host"` for a self-hosted instance |
| `{"github": "...", "version": "1.2.3"}` | Pins a version; ranges (`1.*`, `>=1.2`, `~1.2`, `^1.2`, `latest`) are also accepted |

Load priority, highest first: the project's `Components/` folder, then
`dependencies.json` (with any `environment4d.json` path override), then 4D's
internal components (4D SVG, 4D NetKit, ...). A local `Components/` copy
therefore wins over the declaration, which is the useful escape hatch for
offline work and for CI where a download may be blocked.

Two consequences worth knowing before interpreting logs:

* Under `tool4d`, a declared dependency prints
  `PackageManager No component to fetch dependencies` and
  `PackageManager Dependency 'NAME' cannot be found` on every run, even when
  `Components/NAME.4dbase` is present and the component's classes, methods and
  helpers work. That pair of lines is a package-manager diagnostic, not proof
  that the component failed to load -- call something from the component
  (`cs.Ns.Class.new().version()`) and log the result to get real evidence.
* The language server does not analyse `Components/`, so `check-syntax` reports
  `The class cs.Ns.Class is unknown` for every component class reference. Those
  diagnostics are expected and are not a reason to add placeholder classes to
  the host project. The interpreter/compiler resolve the component normally.

Never commit a populated `Components/` folder that the dependency declaration
reproduces; ignore it and let the Dependency manager or a local install supply
it.
