---
name: 4dtools
description: >
  Download and provision the platform-specific command-line tools required by
  the 4D development skills. Use when a required tool is not available
  locally, or when the skillset needs to initialize its bundled tools.
---

# 4D Tools

## Purpose

This skill provisions the external command-line tools used by the 4D
development skills.

Most tools are distributed as GitHub Release assets from:

`https://github.com/miyako/skills/releases/latest`

Currently the release provides platform-specific builds of:

* `xmllint`
* `boon` (JSON Schema validator)
* `tool4d-lsp-stdio` (4D LSP bridge for code validation)
* `4d-language-classic` (natural-language lookup service for 4D classic-language commands)
* `4d-language-oop` (natural-language lookup service for the 4D object (OOP) language class reference)
* `4d-catalog-diagram` (renders a 4D catalog as an interactive HTML diagram, SVG, or PNG)

`fourdform` is a separate, upstream-only release from the public
[`miyako/4d-form`](https://github.com/miyako/4d-form) repository. It produces
standalone PNG previews of `.4DForm` files and is **macOS universal only**
initially. Use its dedicated procedure below, not the generic asset
pattern or the `miyako/skills` release recipe.

These tools are implementation dependencies of the 4D skills. They are not
themselves 4D skills.

`xsltproc` is also built and published as a release asset (a byproduct of
the same `libxml2`/`libxslt` build that produces `xmllint`), but no
current skill consumes it, so it is intentionally not provisioned or
referenced below. Add it here once a skill actually needs it.

## Installation Location

Downloaded tools must be placed under the `tools/` directory at the root
of the repository being worked on (the repo that contains the 4D
project), not inside the skills repository itself.

Every tool currently provisioned here is used by exactly one 4D skill,
so each is installed into a subdirectory named after that skill, keeping
each skill's tooling isolated -- it can be added, removed, or
reprovisioned without touching what other skills use. If a future tool
is genuinely needed by more than one skill, install it directly under
`tools/` instead of duplicating it per consumer.

| Tool | Destination | Used by |
|------|-------------|---------|
| `xmllint` | `tools/4dcatalog/` | `4dcatalog` only |
| `boon` | `tools/4dform/` | `4dform` only |
| `tool4d-lsp-stdio` | `tools/4dlsp/` | `4dlsp` only |
| `4d-language-classic` | `tools/4dlang/` | `4dlang` only |
| `4d-language-oop` | `tools/4dlang/` | `4dlang` only |
| `4d-catalog-diagram` | `tools/4dcatalog/` | `4dcatalog` only |
| `fourdform` | `tools/4dform/` | `4dform` only; macOS 12+ |

`4d-language-classic` and `4d-language-oop` are natural-language lookup
tools for the two 4D language subsets and are consumed together by the
single `4dlang` skill (see `skills/4dlang/SKILL.md`), so they share one
destination directory rather than each getting its own -- they are not
each `4dlsp`-only the way `tool4d-lsp-stdio` is. (An earlier revision of
this skillset provisioned `4d-language-classic` into `tools/4dlsp/`,
alongside `tool4d-lsp-stdio`, back when `4dlsp` was the only skill doing
language lookup. That mapping no longer matches the "named after the
skill that depends on it" rule below now that `4dlang` owns lookup for
both languages, hence the move.) More precisely: `tools/4dlsp/` named a
*skill*, not a capability, so it became wrong the moment a second
consumer appeared. Two skills both reaching into a directory named after
one of them is how such a path rots, and the rename fixes the naming
defect rather than merely relocating a file.

```
<working-repo>/
  tools/
    4dcatalog/
      xmllint                  (or xmllint.exe on Windows)
      4d-catalog-diagram       (or 4d-catalog-diagram.exe on Windows)
    4dform/
      boon                     (or boon.exe on Windows)
      fourdform                (macOS universal only; no Windows executable)
    4dlsp/
      tool4d-lsp-stdio         (or tool4d-lsp-stdio.exe on Windows)
    4dlang/
      4d-language-classic      (or 4d-language-classic.exe on Windows)
      4d-language-oop          (or 4d-language-oop.exe on Windows)
  Project/
    ...
```

When a new tool is added to this skillset in the future, default to
giving it its own `tools/<skill>/` subdirectory unless it is genuinely
shared by more than one consumer, in which case it stays directly under
`tools/`.

Do not install them globally and do not modify the user's PATH.

Before downloading, confirm the working repo's `.gitignore` ignores the
destination directory of each tool you provision (`/tools/4dcatalog/`,
`/tools/4dform/`, `/tools/4dlsp/`, `/tools/4dlang/`, and `/tools/4dcli/`
for tool4d), and append any missing entry without disturbing existing
ones. The canonical list is in the ".gitignore" section of
`skills/4dproject/SKILL.md`. Do **not** ignore the whole `tools/` folder:
some repositories commit their own scripts there. A provisioned binary
that slips under GitHub's 100 MB per-file limit is accepted and
permanently bloats the repository rather than being rejected.

## Platform Detection

Detect the operating system and CPU architecture before downloading.

On macOS and Linux:

```sh
OS=$(uname -s)     # Darwin or Linux
ARCH=$(uname -m)   # arm64 or x86_64
```

Map to asset name components:

| `uname -s` | `uname -m` | Asset pattern |
|-------------|------------|---------------|
| `Darwin` | `arm64` | `*-macos-arm64.tar.xz` |
| `Darwin` | `x86_64` | `*-macos-x64.tar.xz` |
| `Linux` | `aarch64` | `*-linux-arm64.tar.xz` |
| `Linux` | `x86_64` | `*-linux-x64.tar.xz` |

On Windows (PowerShell):

```powershell
$arch = if ([System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture -eq 'Arm64') { 'arm64' } else { 'x64' }
```

| Architecture | Asset pattern |
|-------------|---------------|
| `x64` | `*-windows-x64.tar.xz` |
| `arm64` | `*-windows-arm64.tar.xz` |

Do not assume that the operating system alone identifies the correct asset.

`fourdform` is the exception to the per-architecture patterns: both
macOS `arm64` and `x86_64` use `fourdform-macos-universal.tar.xz`.
There is no Windows or Linux asset. The generic recipes below apply only
to tools distributed by `miyako/skills`.

## Download and Install Procedure

### fourdform -- pinned upstream macOS universal release

Use Python 3.9+ and Apple's `lipo` (provided by the Command Line Tools).
Run the bundled script from the skillset, passing the **consumer**
repository root, not the `.agents` directory:

```sh
python3 .agents/skills/4dtools/scripts/provision_fourdform.py \
  --repo-root "$PWD"
```

If the skillset is mounted elsewhere, resolve its actual path first.
The script and `release.json` live together under
`skills/4dtools/scripts/` relative to the skillset root.

The pin is upstream **v0.1.0**, executable `fourdform 0.1.0`, macOS
**12.0+**, universal `arm64` + `x86_64`. The release archive is
`fourdform-macos-universal.tar.xz`, containing the root executable
`fourdform`. Its SHA-256 is read from that release's `SHA256SUMS`;
the installer also checks GitHub asset digests when provided and requires
the upstream `release.json` asset to match the committed manifest pin. No
checksum is guessed or embedded in these instructions.

The root-only executable embeds the product and shared-library MIT
notices. Run `tools/4dform/fourdform --license` to display them; no extra
license-file extraction or source download is required.

The script rejects unsupported platforms before any download, selects
the exact pinned asset, verifies checksums before extracting only the
regular executable, checks both architectures, `--version` and the
required `--help` options, then atomically installs it into
`tools/4dform/fourdform`. It appends only `/tools/4dform/` to the consumer
`.gitignore` if needed, after existing rules so a later negation cannot
accidentally expose the binary to Git. It does not alter PATH or install inside `.agents`.
A compatible existing executable is reused without downloading; an
incompatible one is retained and reported. Use `--replace` to explicitly
reprovision, with the old binary retained if verification fails.

The initial upstream release is **ad-hoc signed, not Developer ID signed
or notarized**. The installer does not strip quarantine, disable
Gatekeeper, re-sign the executable, or silently bypass macOS security.
If macOS blocks execution, report the error and stop; do not claim that
installation succeeded or prescribe an automatic bypass.

**Windows is unavailable**, not a downloadable stub. The actual port
boundary and implementation handover are documented at
[Windows handover](https://github.com/miyako/4d-form/blob/main/docs/WINDOWS-HANDOVER.md).
Linux is also unavailable. Do not select a different platform, compile
automatically, or substitute an HTML output for the requested PNG.

After installation, follow `skills/4dform/SKILL.md` to render a `.4DForm`
path and verify that the output really is PNG. No 4D/tool4d runtime or
startup method is needed.

### macOS and Linux

Complete recipe to provision a tool (e.g., `xmllint` for the `4dcatalog`
skill; every other tool follows the same pattern with its own
`DEST_DIR=tools/<skill>` -- see the destination table above):

```sh
TOOL=xmllint
DEST_DIR=tools/4dcatalog
OS=$(uname -s)
ARCH=$(uname -m)

# Map to asset naming convention
case "$OS" in
  Darwin) PLATFORM=macos ;;
  Linux)  PLATFORM=linux ;;
  *)      echo "Unsupported OS: $OS" >&2; exit 1 ;;
esac

case "$ARCH" in
  arm64|aarch64) ASSET_ARCH=arm64 ;;
  x86_64)        ASSET_ARCH=x64 ;;
  *)             echo "Unsupported arch: $ARCH" >&2; exit 1 ;;
esac

ASSET_PATTERN="${TOOL}-${PLATFORM}-${ASSET_ARCH}"

# Query the GitHub Releases API for the latest release
DOWNLOAD_URL=$(curl -sL \
  "https://api.github.com/repos/miyako/skills/releases/latest" |
  grep -o "\"browser_download_url\": *\"[^\"]*${ASSET_PATTERN}[^\"]*\"" |
  head -1 |
  sed 's/.*": *"\(.*\)"/\1/')

if [ -z "$DOWNLOAD_URL" ]; then
  echo "No asset matching ${ASSET_PATTERN} found" >&2
  exit 1
fi

# Download and extract
mkdir -p "$DEST_DIR"
TMP_FILE=$(mktemp)
curl -sL "$DOWNLOAD_URL" -o "$TMP_FILE"
tar -xJf "$TMP_FILE" -C "$DEST_DIR/"
rm -f "$TMP_FILE"

# tar.xz preserves Unix permissions including the execute bit,
# so chmod is not needed.

# On macOS, do NOT modify the binary after extraction --
# it is code-signed and notarized; any modification invalidates
# the signature.

# Verify
"$DEST_DIR/${TOOL}" --version
```

For example, to provision `boon` for the `4dform` skill, set
`TOOL=boon` and `DEST_DIR=tools/4dform`; to provision
`tool4d-lsp-stdio` for `4dlsp`, set `DEST_DIR=tools/4dlsp`; to provision
`4d-language-classic` or `4d-language-oop` for `4dlang`, set
`DEST_DIR=tools/4dlang`. `4d-catalog-diagram` shares `4dcatalog`'s
directory with `xmllint`, so it uses `DEST_DIR=tools/4dcatalog` as
well.

### Windows (PowerShell)

```powershell
$tool = "xmllint"
$destDir = "tools/4dcatalog"
$arch = if ([System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture -eq 'Arm64') { 'arm64' } else { 'x64' }
$pattern = "${tool}-windows-${arch}"

$release = Invoke-RestMethod "https://api.github.com/repos/miyako/skills/releases/latest"
$asset = $release.assets | Where-Object { $_.name -like "*$pattern*" } | Select-Object -First 1

if (-not $asset) {
    Write-Error "No asset matching $pattern found"
    exit 1
}

New-Item -ItemType Directory -Force -Path $destDir | Out-Null
$tmp = [System.IO.Path]::GetTempFileName()
Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $tmp
tar -xJf $tmp -C "$destDir/"
Remove-Item $tmp

# Verify
& "$destDir/${tool}.exe" --version
```

As above, set `$destDir = "tools/4dform"` for `boon`,
`$destDir = "tools/4dlsp"` for `tool4d-lsp-stdio`, or
`$destDir = "tools/4dlang"` for `4d-language-classic`/`4d-language-oop`.

## Provisioning Multiple Tools

Repeat the download recipe for each required tool. Do not batch-download
tools that are not needed by the current operation.

Common sets:

- 4dcatalog needs: `xmllint` (`tools/4dcatalog/xmllint`) for validation, and
  `4d-catalog-diagram` (`tools/4dcatalog/4d-catalog-diagram`) only when the
  user asks to see or diagram the schema. Validation is far more common than
  visualisation, so do not provision the diagram tool pre-emptively.
- 4dform needs: `boon` (`tools/4dform/boon`) for validation, and `fourdform`
  (`tools/4dform/fourdform`, macOS 12+ only) for standalone PNG previews
- 4dlsp needs: `tool4d-lsp-stdio` (`tools/4dlsp/tool4d-lsp-stdio`,
  macOS and Windows only -- no Linux build)
- 4dlang needs: `4d-language-classic` (`tools/4dlang/4d-language-classic`,
  all platforms) and `4d-language-oop`
  (`tools/4dlang/4d-language-oop`, all platforms)

## Verification

After installation, verify each tool can run:

```sh
tools/4dcatalog/xmllint --version
tools/4dcatalog/4d-catalog-diagram --version
tools/4dform/boon --help
# macOS only
tools/4dform/fourdform --version
tools/4dform/fourdform --help
tools/4dlsp/tool4d-lsp-stdio --version
tools/4dlang/4d-language-classic --help
tools/4dlang/4d-language-oop --help
```

On Windows, append `.exe` for available tools; `fourdform` has no Windows build:

```powershell
& tools\4dcatalog\xmllint.exe --version
& tools\4dcatalog\4d-catalog-diagram.exe --version
& tools\4dform\boon.exe --help
& tools\4dlsp\tool4d-lsp-stdio.exe --version
& tools\4dlang\4d-language-classic.exe --help
& tools\4dlang\4d-language-oop.exe --help
```

A successful download is not sufficient. Treat installation as successful
only after the executable can be launched.

## Existing Tools

Before downloading, check whether the required tool is already available
on the host:

```sh
command -v xmllint >/dev/null 2>&1 && xmllint --version
```

If the system tool is acceptable for the current operation, it may be used
instead of downloading another copy.

If the 4D skill requires the known bundled version, use the copy at its
destination under `tools/` (see the destination table above) after
provisioning it.

Do not overwrite a working bundled executable unnecessarily.

## Failure Handling

If no release asset matches the current platform and architecture:

* do not download a different architecture;
* do not attempt to compile the tool automatically;
* report the detected platform and architecture;
* report the available matching information when possible;
* stop with a clear error.

If `curl` is unavailable, report the problem rather than silently switching
to an unrelated package manager.

If the download succeeds but the executable cannot be launched, do not
report the tool as installed.

## Security

Only download assets from the specified GitHub repository and release:
`miyako/skills` for the generic recipes, or pinned `miyako/4d-form` for
`fourdform`.

Do not execute arbitrary files downloaded from other URLs.

When the release provides checksums or GitHub asset digests, verify the
download before installing it.

Use a temporary file for downloads and install only after verification.

## Use by Other Skills

Other 4D skills should not contain their own download logic. They reference
this skill when a tool is unavailable.

The dependency relationships are:

```
4dcatalog --> xmllint             --> 4dtools provisions tools/4dcatalog/xmllint
4dform    --> boon                --> 4dtools provisions tools/4dform/boon
4dform    --> fourdform           --> 4dtools provisions tools/4dform/fourdform (macOS only)
4dlsp     --> tool4d-lsp-stdio    --> 4dtools provisions tools/4dlsp/tool4d-lsp-stdio
4dlang    --> 4d-language-classic --> 4dtools provisions tools/4dlang/4d-language-classic
4dlang    --> 4d-language-oop     --> 4dtools provisions tools/4dlang/4d-language-oop
```

The individual 4D skills should concentrate on 4D-specific behavior,
schemas, validation rules, and workflows rather than duplicating tool
installation logic.
