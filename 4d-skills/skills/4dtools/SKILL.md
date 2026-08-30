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
* `xsltproc`
* `boon` (JSON Schema validator)
* `tool4d-lsp-stdio` (4D LSP bridge for code validation)

These tools are implementation dependencies of the 4D skills. They are not
themselves 4D skills.

## Installation Location

Downloaded tools must be placed in the `tools/` directory at the root of
the repository being worked on (the repo that contains the 4D project),
not inside the skills repository itself.

```
<working-repo>/
  tools/
    xmllint        (or xmllint.exe on Windows)
    xsltproc       (or xsltproc.exe on Windows)
    boon           (or boon.exe on Windows)
    tool4d-lsp-stdio (or tool4d-lsp-stdio.exe on Windows)
  Project/
    ...
```

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

Complete recipe to provision a tool (e.g., `xmllint`):

```sh
TOOL=xmllint
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
mkdir -p tools
TMP_FILE=$(mktemp)
curl -sL "$DOWNLOAD_URL" -o "$TMP_FILE"
tar -xJf "$TMP_FILE" -C tools/
rm -f "$TMP_FILE"

# tar.xz preserves Unix permissions including the execute bit,
# so chmod is not needed.

# On macOS, do NOT modify the binary after extraction --
# it is code-signed and notarized; any modification invalidates
# the signature.

# Verify
tools/${TOOL} --version
```

### Windows (PowerShell)

```powershell
$tool = "xmllint"
$arch = if ([System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture -eq 'Arm64') { 'arm64' } else { 'x64' }
$pattern = "${tool}-windows-${arch}"

$release = Invoke-RestMethod "https://api.github.com/repos/miyako/skills/releases/latest"
$asset = $release.assets | Where-Object { $_.name -like "*$pattern*" } | Select-Object -First 1

if (-not $asset) {
    Write-Error "No asset matching $pattern found"
    exit 1
}

New-Item -ItemType Directory -Force -Path tools | Out-Null
$tmp = [System.IO.Path]::GetTempFileName()
Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $tmp
tar -xJf $tmp -C tools/
Remove-Item $tmp

# Verify
& "tools/${tool}.exe" --version
```

## Provisioning Multiple Tools

Repeat the download recipe for each required tool. Do not batch-download
tools that are not needed by the current operation.

Common sets:

- 4dcatalog needs: `xmllint`
- 4dform needs: `boon`
- 4dlsp needs: `tool4d-lsp-stdio` (macOS and Windows only -- no Linux build)
- XSLT transforms need: `xsltproc`

## Verification

After installation, verify each tool can run:

```sh
tools/xmllint --version
tools/xsltproc --version
tools/boon --help
```

On Windows, append `.exe`:

```powershell
& tools\xmllint.exe --version
& tools\xsltproc.exe --version
& tools\boon.exe --help
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

If the 4D skill requires the known bundled version, use the copy in
`tools/` after provisioning it.

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
4dcatalog       --> xmllint      --> 4dtools provisions xmllint
4dform          --> boon         --> 4dtools provisions boon
XSLT transforms --> xsltproc    --> 4dtools provisions xsltproc
```

The individual 4D skills should concentrate on 4D-specific behavior,
schemas, validation rules, and workflows rather than duplicating tool
installation logic.
