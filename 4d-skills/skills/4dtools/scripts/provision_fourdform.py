#!/usr/bin/env python3
"""Install the pinned upstream fourdform release into a consumer repository."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from urllib.error import URLError
from urllib.request import Request, urlopen


MANIFEST = Path(__file__).with_name("release.json")
DESTINATION = Path("tools/4dform/fourdform")


class ProvisionError(Exception):
    pass


def load_manifest(path):
    source = json.loads(path.read_text())
    if source["schemaVersion"] != 1 or source["executable"] != "fourdform":
        raise ProvisionError("Unsupported fourdform release manifest")
    macos = source["platforms"]["macos-universal"]
    return {
        "source": source,
        "repository": "miyako/4d-form",
        "version": source["version"],
        "release_tag": source["tag"],
        "asset": macos["archive"],
        "binary": macos["binary"],
        "checksum_asset": macos["checksumFile"],
        "macos_minimum": macos["minimumOS"],
        "windows_handover": (
            "https://github.com/miyako/4d-form/blob/main/docs/WINDOWS-HANDOVER.md"
        ),
    }


def fetch(url, destination):
    request = Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "miyako-skills-fourdform-provisioner",
    })
    with urlopen(request, timeout=60) as response, destination.open("wb") as output:
        shutil.copyfileobj(response, output)


def check_platform(manifest):
    system, machine = platform.system(), platform.machine()
    if system != "Darwin":
        detail = f"Windows handover: {manifest['windows_handover']}" if system == "Windows" else (
            "No Linux release is available."
        )
        raise ProvisionError(
            f"fourdform is unavailable on {system}/{machine}; macOS only. {detail}"
        )
    if machine not in ("arm64", "x86_64"):
        raise ProvisionError(f"Unsupported macOS architecture: {machine}")
    current = tuple(int(part) for part in platform.mac_ver()[0].split("."))
    minimum = tuple(int(part) for part in manifest["macos_minimum"].split("."))
    if current < minimum:
        raise ProvisionError(f"fourdform requires macOS {manifest['macos_minimum']} or newer")


def run(arguments):
    result = subprocess.run(
        [str(arg) for arg in arguments], capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise ProvisionError(
            f"{arguments[0]} failed ({result.returncode}): "
            f"{result.stderr.strip() or result.stdout.strip()}"
        )
    return result.stdout.strip()


def verify_binary(binary, manifest):
    architectures = set(run(["lipo", "-archs", binary]).split())
    if not {"arm64", "x86_64"}.issubset(architectures):
        raise ProvisionError("Release binary is not macOS universal (arm64 + x86_64)")
    version = run([binary, "--version"])
    if version != f"fourdform {manifest['version']}":
        raise ProvisionError(f"Unexpected fourdform version: {version!r}")
    help_text = run([binary, "--help"])
    for flag in ("--output", "--theme", "--page", "--scale", "--max-dimension", "--language"):
        if flag not in help_text:
            raise ProvisionError(f"Installed fourdform --help is missing {flag}")


def select_asset(release, manifest):
    if release.get("tag_name") != manifest["release_tag"] or release.get("draft"):
        raise ProvisionError("Release metadata does not match the pinned published tag")
    return release_asset(release, manifest, manifest["asset"])


def release_asset(release, manifest, name):
    matches = [
        asset for asset in release.get("assets", [])
        if asset.get("name") == name
    ]
    if len(matches) != 1:
        raise ProvisionError(f"Expected exactly one release asset named {name}")
    asset = matches[0]
    prefix = (
        f"https://github.com/{manifest['repository']}/releases/download/"
        f"{manifest['release_tag']}/"
    )
    if asset.get("browser_download_url") != prefix + name:
        raise ProvisionError("Release asset URL is outside the pinned upstream release")
    digest = asset.get("digest")
    if digest is not None and (
        not isinstance(digest, str) or not re.fullmatch(r"sha256:[0-9a-fA-F]{64}", digest)
    ):
        raise ProvisionError(f"Unusable GitHub SHA-256 digest for {name}")
    return asset


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_digest(path, asset):
    if asset.get("digest") and sha256(path) != asset["digest"].split(":", 1)[1].lower():
        raise ProvisionError(f"GitHub SHA-256 mismatch for {asset['name']}; nothing installed")


def archive_checksum(checksums, name):
    matches = []
    for line in checksums.read_text().splitlines():
        match = re.fullmatch(r"([0-9a-fA-F]{64}) [ *](.+)", line)
        if match and match[2] == name:
            matches.append(match[1].lower())
    if len(matches) != 1:
        raise ProvisionError(f"SHA256SUMS must contain exactly one checksum for {name}")
    return matches[0]


def extract_binary(archive, binary, manifest):
    with tarfile.open(archive, "r:xz") as package:
        matches = [member for member in package.getmembers() if member.name == manifest["binary"]]
        if len(matches) != 1 or not matches[0].isfile():
            raise ProvisionError("Archive must contain exactly one regular fourdform binary")
        member = matches[0]
        if not member.mode & 0o111:
            raise ProvisionError("Archive binary does not have executable permissions")
        with package.extractfile(member) as source, binary.open("wb") as output:
            shutil.copyfileobj(source, output)
        binary.chmod(member.mode & 0o755)


def ensure_ignore(root):
    ignore = root / ".gitignore"
    if ignore.is_symlink():
        raise ProvisionError("Refusing to modify a symlinked .gitignore")
    text = ignore.read_text() if ignore.exists() else ""
    if "/tools/4dform/" not in text.splitlines():
        with ignore.open("a") as output:
            if text and not text.endswith("\n"):
                output.write("\n")
            output.write("/tools/4dform/\n")


def provision(root, manifest, replace=False):
    check_platform(manifest)
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ProvisionError(f"Consumer repository root is not a directory: {root}")
    destination = root / DESTINATION
    for path in (root / "tools", destination.parent, destination):
        if path.is_symlink():
            raise ProvisionError(f"Refusing a symlinked installation path: {path}")
    if destination.exists() and not replace:
        try:
            verify_binary(destination, manifest)
        except ProvisionError as error:
            raise ProvisionError(
                f"Existing fourdform is incompatible: {error}. Use --replace to reprovision."
            ) from error
        ensure_ignore(root)
        return destination

    with tempfile.TemporaryDirectory(prefix="fourdform-download-") as temporary:
        temporary = Path(temporary)
        metadata = temporary / "release.json"
        fetch(
            f"https://api.github.com/repos/{manifest['repository']}/releases/tags/"
            f"{manifest['release_tag']}", metadata
        )
        release = json.loads(metadata.read_text())
        asset = select_asset(release, manifest)
        manifest_asset = release_asset(release, manifest, "release.json")
        upstream_manifest = temporary / "upstream-release.json"
        fetch(manifest_asset["browser_download_url"], upstream_manifest)
        verify_digest(upstream_manifest, manifest_asset)
        if load_manifest(upstream_manifest) != manifest:
            raise ProvisionError("Upstream release.json differs from the committed release pin")
        checksum_asset = release_asset(release, manifest, manifest["checksum_asset"])
        checksums = temporary / manifest["checksum_asset"]
        fetch(checksum_asset["browser_download_url"], checksums)
        verify_digest(checksums, checksum_asset)
        expected = archive_checksum(checksums, manifest["asset"])
        archive = temporary / manifest["asset"]
        fetch(asset["browser_download_url"], archive)
        verify_digest(archive, asset)
        if sha256(archive) != expected:
            raise ProvisionError("Release archive SHA-256 mismatch; nothing installed")
        binary = temporary / "fourdform"
        extract_binary(archive, binary, manifest)
        verify_binary(binary, manifest)
        ensure_ignore(root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".fourdform-", dir=destination.parent) as stage:
            staged = Path(stage) / "fourdform"
            shutil.copy2(binary, staged)
            os.replace(staged, destination)
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path, help="consumer repository root")
    parser.add_argument("--replace", action="store_true", help="replace an existing binary after verification")
    arguments = parser.parse_args()
    try:
        manifest = load_manifest(MANIFEST)
        destination = provision(arguments.repo_root, manifest, arguments.replace)
    except (ProvisionError, OSError, ValueError, KeyError, TypeError, URLError,
            tarfile.TarError, subprocess.TimeoutExpired) as error:
        print(f"fourdform provisioning failed: {error}", file=sys.stderr)
        return 1
    print(f"Installed fourdform {manifest['version']}: {destination}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
