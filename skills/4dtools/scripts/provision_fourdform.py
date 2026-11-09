#!/usr/bin/env python3
"""Install fourdform from the latest skills release into a consumer repository."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import stat
import struct
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from urllib.error import URLError
from urllib.request import Request, urlopen


MANIFEST = Path(__file__).with_name("release.json")
DESTINATION = Path("tools/4dform/fourdform")


class ProvisionError(Exception):
    pass


def load_manifest(path):
    source = json.loads(path.read_text())
    if (source["schemaVersion"] != 1 or source["executable"] != "fourdform"
            or source["repository"] != "miyako/skills" or source["release"] != "latest"):
        raise ProvisionError("Unsupported fourdform release manifest")
    return {
        "repository": source["repository"],
        "version": source["version"],
        "platforms": source["platforms"],
        "checksum_asset": source["checksumFile"],
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
    if system not in ("Darwin", "Windows"):
        raise ProvisionError(
            f"fourdform is unavailable on {system}/{machine}; macOS and Windows only."
        )
    architecture = {"arm64": "arm64", "aarch64": "arm64",
                    "amd64": "x86_64", "x86_64": "x86_64"}.get(machine.lower())
    label = "macOS" if system == "Darwin" else "Windows"
    if architecture is None:
        raise ProvisionError(f"Unsupported {label} architecture: {machine}")
    key = ("macos" if system == "Darwin" else "windows") + (
        "-arm64" if architecture == "arm64" else "-x64"
    )
    selected = manifest["platforms"][key]
    version = platform.mac_ver()[0] if system == "Darwin" else platform.win32_ver()[1]
    current = tuple(int(part) for part in version.split("."))
    minimum = tuple(int(part) for part in selected["minimumOS"].split("."))
    if current < minimum:
        raise ProvisionError(f"fourdform requires {label} {selected['minimumOS']} or newer")
    return dict(manifest, asset=selected["archive"], binary=selected["binary"],
                architecture=selected["architecture"], system=system)


def run(arguments):
    result = subprocess.run(
        [str(arg) for arg in arguments], capture_output=True, text=True,
        encoding="utf-8", timeout=30
    )
    if result.returncode != 0:
        raise ProvisionError(
            f"{arguments[0]} failed ({result.returncode}): "
            f"{result.stderr.strip() or result.stdout.strip()}"
        )
    return result.stdout.strip()


def verify_binary(binary, manifest):
    if manifest["system"] == "Windows":
        verify_pe(binary, manifest["architecture"])
    else:
        architectures = set(run(["lipo", "-archs", binary]).split())
        if manifest["architecture"] not in architectures:
            raise ProvisionError(
                f"Release binary does not support macOS {manifest['architecture']}"
            )
    version = run([binary, "--version"])
    if version != f"fourdform {manifest['version']}":
        raise ProvisionError(f"Unexpected fourdform version: {version!r}")
    help_text = run([binary, "--help"])
    for flag in ("--output", "--theme", "--page", "--scale", "--max-dimension", "--language"):
        if flag not in help_text:
            raise ProvisionError(f"Installed fourdform --help is missing {flag}")


def verify_pe(binary, architecture):
    with binary.open("rb") as image:
        header = image.read(64)
        if len(header) != 64 or header[:2] != b"MZ":
            raise ProvisionError(f"Invalid Windows PE image: {binary.name}")
        image.seek(struct.unpack_from("<I", header, 60)[0])
        signature = image.read(6)
    expected = {"x86_64": 0x8664, "arm64": 0xAA64}[architecture]
    if (len(signature) != 6 or signature[:4] != b"PE\0\0"
            or struct.unpack_from("<H", signature, 4)[0] != expected):
        raise ProvisionError(f"Release image {binary.name} does not support Windows {architecture}")


def select_asset(release, manifest):
    tag = release.get("tag_name")
    if (not isinstance(tag, str) or not re.fullmatch(r"[A-Za-z0-9._-]+", tag)
            or release.get("draft") or release.get("prerelease")):
        raise ProvisionError("Release metadata is not a published stable skills release")
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
        f"{release['tag_name']}/"
    )
    if asset.get("browser_download_url") != prefix + name:
        raise ProvisionError("Release asset URL is outside the selected skills release")
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
    if manifest["system"] == "Windows":
        with zipfile.ZipFile(archive) as package:
            members = package.infolist()
            names = [member.filename for member in members]
            if (names.count(manifest["binary"]) != 1
                    or names.count("WebView2-SDK-LICENSE.txt") != 1
                    or len({name.casefold() for name in names}) != len(names)):
                raise ProvisionError("Windows archive must contain one binary and WebView2 notice")
            for member in members:
                name = member.filename
                mode = member.external_attr >> 16
                if (not re.fullmatch(r"[A-Za-z0-9_.-]+", name)
                        or name in (".", "..") or member.is_dir()
                        or stat.S_IFMT(mode) not in (0, stat.S_IFREG)
                        or not (name in (manifest["binary"], "WebView2-SDK-LICENSE.txt")
                                or name.lower().endswith(".dll"))):
                    raise ProvisionError(f"Unexpected Windows archive member: {name}")
            for member in members:
                target = binary.parent / member.filename
                with package.open(member) as source, target.open("wb") as output:
                    shutil.copyfileobj(source, output)
                if target.suffix.lower() == ".dll":
                    verify_pe(target, manifest["architecture"])
        return
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
    text = ignore.read_text(encoding="utf-8") if ignore.exists() else ""
    patterns = [line for line in text.splitlines() if line and not line.startswith("#")]
    if not patterns or patterns[-1] != "/tools/4dform/":
        with ignore.open("a", encoding="utf-8") as output:
            if text and not text.endswith("\n"):
                output.write("\n")
            output.write("/tools/4dform/\n")


def provision(root, manifest, replace=False, fetcher=None):
    manifest = check_platform(manifest)
    download = fetch if fetcher is None else fetcher
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ProvisionError(f"Consumer repository root is not a directory: {root}")
    destination = root / DESTINATION.parent / manifest["binary"]
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
        download(
            f"https://api.github.com/repos/{manifest['repository']}/releases/latest",
            metadata
        )
        release = json.loads(metadata.read_text())
        asset = select_asset(release, manifest)
        checksum_asset = release_asset(release, manifest, manifest["checksum_asset"])
        checksums = temporary / manifest["checksum_asset"]
        download(checksum_asset["browser_download_url"], checksums)
        verify_digest(checksums, checksum_asset)
        expected = archive_checksum(checksums, manifest["asset"])
        archive = temporary / manifest["asset"]
        download(asset["browser_download_url"], archive)
        verify_digest(archive, asset)
        if sha256(archive) != expected:
            raise ProvisionError("Release archive SHA-256 mismatch; nothing installed")
        payload = temporary / "payload"
        payload.mkdir()
        binary = payload / manifest["binary"]
        extract_binary(archive, binary, manifest)
        verify_binary(binary, manifest)
        for source in payload.iterdir():
            target = destination.parent / source.name
            if target.is_symlink() or (target.exists() and not target.is_file()):
                raise ProvisionError(f"Refusing an unsafe installation path: {target}")
        ensure_ignore(root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".fourdform-", dir=destination.parent) as stage:
            stage = Path(stage)
            backups = stage / "backups"
            backups.mkdir()
            installed = []
            try:
                for source in sorted(payload.iterdir(), key=lambda path: path == binary):
                    staged = stage / source.name
                    target = destination.parent / source.name
                    shutil.copy2(source, staged)
                    if target.exists():
                        shutil.copy2(target, backups / source.name)
                    os.replace(staged, target)
                    installed.append(target)
            except OSError:
                for target in reversed(installed):
                    backup = backups / target.name
                    if backup.exists():
                        os.replace(backup, target)
                    else:
                        target.unlink()
                raise
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
            tarfile.TarError, zipfile.BadZipFile, subprocess.TimeoutExpired) as error:
        print(f"fourdform provisioning failed: {error}", file=sys.stderr)
        return 1
    print(f"Installed fourdform {manifest['version']}: {destination}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
