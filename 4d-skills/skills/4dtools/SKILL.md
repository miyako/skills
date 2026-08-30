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

These tools are implementation dependencies of the 4D skills. They are not
themselves 4D skills.

## Installation Location

Downloaded tools must be placed in the repository-level:

```
tools/
```

Do not install them globally and do not modify the user's PATH.

After installation, the expected layout is:

```
tools/
	xmllint
	xsltproc
```

On Windows, executable files may use the `.exe` extension.

## Platform Detection

Determine the host operating system and CPU architecture before downloading.

Supported targets are the platform/architecture combinations provided by the
release.

At minimum distinguish:

* macOS arm64
* macOS x86_64
* Windows x86_64
* Linux x86_64

Do not assume that the operating system alone identifies the correct asset.

On macOS, distinguish Apple Silicon (`arm64`) from Intel (`x86_64`).

On Windows, distinguish the native architecture rather than assuming the
architecture of the shell.

## Download Procedure

Prefer `curl` for downloading release assets.

Use the latest release.

Do not silently substitute an arbitrary file from the repository's `main`
branch.

Use the GitHub Releases API to discover the assets for the latest release
rather than relying on guessed asset filenames.

The GitHub release API endpoint is:

```
https://api.github.com/repos/miyako/skills/releases/latest
```

Select the asset whose name matches:

1. the required tool;
2. the current operating system;
3. the current CPU architecture.

Do not download an asset intended for another platform or architecture.

## Installation

Create the repository `tools/` directory if necessary.

Download to a temporary file first.

Do not overwrite an existing working executable until the download has
completed successfully.

After a successful download:

1. Move the executable into `tools/`.
2. On Unix-like systems, ensure it has executable permissions.
3. On macOS, preserve the downloaded executable's code-signing/notarization
   state. Do not modify the executable after download.
4. On Windows, retain the `.exe` extension.
5. Invoke the installed executable once to verify that it can run.

## Verification

After installation, run:

```
tools/xmllint --version
```

and/or:

```
tools/xsltproc --version
```

The command should successfully execute and print its version information.

A successful download is not sufficient. Treat installation as successful
only after the executable can be launched.

Log the following information:

* tool name
* detected operating system
* detected architecture
* release tag
* selected asset name
* download URL
* destination
* reported tool version

Do not log secrets or environment variables.

## Existing Tools

Before downloading, check whether the required tool is already available on
the host.

If the system tool is acceptable for the current operation, it may be used
instead of downloading another copy.

If the 4D skill requires the known bundled version, use the copy in `tools/`
after provisioning it.

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

If the download succeeds but the executable cannot be launched, do not report
the tool as installed.

## Security

Only download assets from the specified GitHub repository and release.

Do not execute arbitrary files downloaded from other URLs.

When the release provides checksums or GitHub asset digests, verify the
download before installing it.

Use a temporary file for downloads and install only after verification.

## Use by Other Skills

Other 4D skills should not contain their own download logic.

For example, the `4d-form` skill may require `xmllint` and should instruct
the agent to use this skill when `xmllint` is unavailable.

The dependency relationship is:

```
4d-form
	|
	+-- requires xmllint
			|
			+-- 4d-tools provisions xmllint
```

Likewise:

```
4d-catalog
	|
	+-- requires xmllint

4d-form
	|
	+-- may require xsltproc
```

The individual 4D skills should concentrate on 4D-specific behavior,
schemas, validation rules, and workflows rather than duplicating tool
installation logic.
