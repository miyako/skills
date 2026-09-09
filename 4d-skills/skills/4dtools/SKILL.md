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

The tools are distributed as GitHub Release assets from:

`https://github.com/miyako/skills/releases/latest`

Currently the release provides platform-specific builds of:

* `xmllint`
* `boon` (JSON Schema validator)
* `tool4d-lsp-stdio` (4D LSP bridge for code validation)
* `4d-language-classic` (natural-language lookup service for 4D classic-language commands)
* `4d-language-oop` (natural-language lookup service for the 4D object (OOP) language class reference)
* `4d-catalog-diagram` (renders a 4D catalog as an interactive HTML diagram, SVG, or PNG)

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

## Download and Install Procedure

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
- 4dform needs: `boon` (`tools/4dform/boon`)
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
tools/4dlsp/tool4d-lsp-stdio --version
tools/4dlang/4d-language-classic --help
tools/4dlang/4d-language-oop --help
```

On Windows, append `.exe`:

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

Only download assets from the specified GitHub repository and release.

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
4dlsp     --> tool4d-lsp-stdio    --> 4dtools provisions tools/4dlsp/tool4d-lsp-stdio
4dlang    --> 4d-language-classic --> 4dtools provisions tools/4dlang/4d-language-classic
4dlang    --> 4d-language-oop     --> 4dtools provisions tools/4dlang/4d-language-oop
```

The individual 4D skills should concentrate on 4D-specific behavior,
schemas, validation rules, and workflows rather than duplicating tool
installation logic.
