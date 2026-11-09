#!/usr/bin/env python3
"""Offline regression tests for the consumer-side fourdform provisioner."""

import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import struct
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch
import warnings
import zipfile
import zlib


SCRIPT = Path(__file__).resolve().parents[2] / (
    "4d-skills/skills/4dtools/scripts/provision_fourdform.py"
)
sys.dont_write_bytecode = True
SPEC = importlib.util.spec_from_file_location("provision_fourdform", SCRIPT)
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)
SMOKE_SPEC = importlib.util.spec_from_file_location(
    "smoke_fourdform_release", Path(__file__).with_name("smoke_fourdform_release.py")
)
smoke = importlib.util.module_from_spec(SMOKE_SPEC)
SMOKE_SPEC.loader.exec_module(smoke)


def package(members=None):
    output = io.BytesIO()
    if members is None:
        members = [("fourdform", b"fixture binary", 0o755, tarfile.REGTYPE)]
    with tarfile.open(fileobj=output, mode="w:xz") as archive:
        for name, contents, mode, kind in members:
            member = tarfile.TarInfo(name)
            member.mode, member.type = mode, kind
            if kind == tarfile.REGTYPE:
                member.size = len(contents)
                archive.addfile(member, io.BytesIO(contents))
            else:
                member.linkname = "../outside"
                archive.addfile(member)
    return output.getvalue()


def pe_image(architecture="arm64"):
    image = bytearray(70)
    image[:2] = b"MZ"
    struct.pack_into("<I", image, 60, 64)
    image[64:68] = b"PE\0\0"
    struct.pack_into("<H", image, 68, 0xAA64 if architecture == "arm64" else 0x8664)
    return bytes(image)


def windows_package(architecture="arm64", members=None):
    output = io.BytesIO()
    if members is None:
        members = [
            ("fourdform.exe", pe_image(architecture)),
            ("swiftCore.dll", pe_image(architecture)),
            ("vcruntime140.dll", pe_image(architecture)),
            ("WebView2-SDK-LICENSE.txt", b"BSD-3-Clause fixture notice"),
        ]
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Duplicate name:", category=UserWarning)
        with zipfile.ZipFile(output, "w") as archive:
            for name, data in members:
                archive.writestr(name, data)
    return output.getvalue()


class ProvisionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.system = self.mock("platform.system", return_value="Darwin")
        self.machine = self.mock("platform.machine", return_value="arm64")
        self.mac_version = self.mock("platform.mac_ver", return_value=("12.0", (), ""))
        self.manifest = installer.check_platform(installer.load_manifest(installer.MANIFEST))
        self.destination = self.root / installer.DESTINATION
        self.metadata_url = (
            f"https://api.github.com/repos/{self.manifest['repository']}/releases/latest"
        )
        self.prefix = (
            f"https://github.com/{self.manifest['repository']}/releases/download/"
            "v1.2.3/"
        )
        self.run = self.mock("run", side_effect=self.command)
        self.fetch = self.mock("fetch", side_effect=self.download)
        self.set_release(package())

    def mock(self, target, **kwargs):
        if "." in target:
            owner, attribute = target.split(".")
            patcher = patch.object(getattr(installer, owner), attribute, **kwargs)
        else:
            patcher = patch.object(installer, target, **kwargs)
        mocked = patcher.start()
        self.addCleanup(patcher.stop)
        return mocked

    def command(self, arguments):
        if arguments[0] == "lipo":
            return self.machine.return_value
        if arguments[1] == "--version":
            return "fourdform 0.1.0"
        return "--output --theme --page --scale --max-dimension --language"

    def set_release(self, archive):
        checksum = hashlib.sha256(archive).hexdigest()
        sums = f"{checksum}  {self.manifest['asset']}\n".encode()
        self.release = {"tag_name": "v1.2.3", "draft": False, "prerelease": False, "assets": [
            {"name": name, "browser_download_url": self.prefix + name,
             "digest": "sha256:" + hashlib.sha256(data).hexdigest()}
            for name, data in (
                (self.manifest["asset"], archive), ("SHA256SUMS", sums)
            )
        ]}
        self.downloads = {
            self.prefix + self.manifest["asset"]: archive,
            self.prefix + "SHA256SUMS": sums,
        }

    def download(self, url, destination):
        data = json.dumps(self.release).encode() if url == self.metadata_url else self.downloads[url]
        destination.write_bytes(data)

    def provision(self, replace=False):
        return installer.provision(self.root, self.manifest, replace)

    def assert_untouched(self):
        self.assertFalse(self.destination.exists())
        self.assertFalse((self.root / ".gitignore").exists())
        self.run.assert_not_called()

    def test_install_and_scoped_ignore_preserve_existing_scripts(self):
        (self.root / "tools").mkdir()
        script = self.root / "tools" / "project.sh"
        script.write_text("echo project\n")
        (self.root / ".gitignore").write_text("existing-entry")
        self.assertEqual(self.provision(), self.destination)
        self.assertEqual(self.destination.read_bytes(), b"fixture binary")
        if sys.platform != "win32":  # Windows has no POSIX execute bits
            self.assertEqual(self.destination.stat().st_mode & 0o777, 0o755)
        self.assertEqual((self.root / ".gitignore").read_text(), "existing-entry\n/tools/4dform/\n")
        self.assertEqual(script.read_text(), "echo project\n")
        self.assertEqual(self.fetch.call_count, 3)

    def test_both_macos_architectures_select_matching_skills_archive(self):
        for machine in ("arm64", "x86_64"):
            with self.subTest(machine=machine):
                self.machine.return_value = machine
                self.manifest = installer.check_platform(self.manifest)
                expected = "fourdform-macos-arm64.tar.xz" if machine == "arm64" else (
                    "fourdform-macos-x64.tar.xz"
                )
                self.assertEqual(self.manifest["asset"], expected)
                self.set_release(package())
                self.provision(replace=True)
                self.assertEqual(self.fetch.call_args[0][0], self.prefix + self.manifest["asset"])
                self.assertEqual(self.fetch.call_args_list[-3][0][0], self.metadata_url)

    def test_unsupported_systems_fail_before_download_with_no_fake_binary(self):
        for system in ("Linux", "Other"):
            with self.subTest(system=system):
                self.system.return_value = system
                with self.assertRaises(installer.ProvisionError) as raised:
                    self.provision()
                self.assertIn("unavailable", str(raised.exception))
                self.fetch.assert_not_called()
                self.assert_untouched()

    def test_old_macos_and_unknown_architecture_fail_before_download(self):
        self.mac_version.return_value = ("11.7", (), "")
        with self.assertRaisesRegex(installer.ProvisionError, "requires macOS 12.0"):
            self.provision()
        self.mac_version.return_value = ("12.0", (), "")
        self.machine.return_value = "other"
        with self.assertRaisesRegex(installer.ProvisionError, "Unsupported macOS architecture"):
            self.provision()
        self.fetch.assert_not_called()
        self.assert_untouched()

    def test_reuses_compatible_binary_without_download_or_duplicate_ignore(self):
        self.provision()
        self.fetch.reset_mock()
        self.provision()
        self.fetch.assert_not_called()
        self.assertEqual((self.root / ".gitignore").read_text(), "/tools/4dform/\n")

    def test_later_negated_ignore_rule_is_overridden_without_rewriting_user_rules(self):
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True, capture_output=True)
        text = "/tools/4dform/\n!/tools/4dform/\n# user comment\n"
        (self.root / ".gitignore").write_text(text)
        self.provision()
        self.assertEqual((self.root / ".gitignore").read_text(), text + "/tools/4dform/\n")
        result = subprocess.run(
            ["git", "-C", str(self.root), "check-ignore", "--quiet", "--no-index",
             "tools/4dform/fourdform"], capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.provision()
        self.assertEqual((self.root / ".gitignore").read_text(), text + "/tools/4dform/\n")

    def test_incompatible_existing_binary_is_retained_without_replace(self):
        self.destination.parent.mkdir(parents=True)
        self.destination.write_bytes(b"old binary")
        self.run.side_effect = lambda args: (
            "fourdform 0.0.1" if args[1] == "--version" else self.command(args)
        )
        with self.assertRaisesRegex(installer.ProvisionError, "Use --replace"):
            self.provision()
        self.assertEqual(self.destination.read_bytes(), b"old binary")
        self.fetch.assert_not_called()

    def test_failed_replacement_retains_old_binary(self):
        self.destination.parent.mkdir(parents=True)
        self.destination.write_bytes(b"old binary")
        self.downloads[self.prefix + self.manifest["asset"]] = b"corrupt archive"
        with self.assertRaisesRegex(installer.ProvisionError, "SHA-256 mismatch"):
            self.provision(replace=True)
        self.assertEqual(self.destination.read_bytes(), b"old binary")
        self.run.assert_not_called()
        self.assertFalse((self.root / ".gitignore").exists())

    def test_checksum_required_even_without_github_digest(self):
        for asset in self.release["assets"]:
            asset["digest"] = None
        self.provision()
        self.assertTrue(self.destination.is_file())

    def test_missing_checksum_asset_is_rejected(self):
        self.release["assets"].pop(1)
        with self.assertRaisesRegex(installer.ProvisionError, "SHA256SUMS"):
            self.provision()
        self.assert_untouched()

    def test_existing_universal_binary_can_be_reused(self):
        self.provision()
        self.fetch.reset_mock()
        self.run.side_effect = lambda args: (
            "x86_64 arm64" if args[0] == "lipo" else self.command(args)
        )
        self.provision()
        self.fetch.assert_not_called()

    def test_missing_wrong_and_duplicate_checksums_are_rejected(self):
        for sums in (b"", b"not a checksum\n", (
            self.downloads[self.prefix + "SHA256SUMS"] * 2
        )):
            with self.subTest(sums=sums):
                self.release["assets"][1]["digest"] = None
                self.downloads[self.prefix + "SHA256SUMS"] = sums
                with self.assertRaisesRegex(installer.ProvisionError, "exactly one checksum"):
                    self.provision()
                self.assert_untouched()

    def test_checksum_mismatch_without_github_digest_is_rejected(self):
        self.release["assets"][0]["digest"] = None
        self.downloads[self.prefix + self.manifest["asset"]] = b"corrupt archive"
        with self.assertRaisesRegex(installer.ProvisionError, "archive SHA-256 mismatch"):
            self.provision()
        self.assert_untouched()

    def test_checksum_asset_github_digest_is_verified(self):
        self.downloads[self.prefix + "SHA256SUMS"] = b"corrupt checksum file"
        with self.assertRaisesRegex(installer.ProvisionError, "GitHub SHA-256 mismatch"):
            self.provision()
        self.assert_untouched()

    def test_untrusted_url_wrong_tag_and_draft_are_rejected(self):
        for field, value in (("tag_name", ""), ("tag_name", "../other"),
                             ("draft", True), ("prerelease", True)):
            with self.subTest(field=field):
                original = self.release[field]
                self.release[field] = value
                with self.assertRaisesRegex(installer.ProvisionError, "published stable"):
                    self.provision()
                self.release[field] = original
        self.release["assets"][0]["browser_download_url"] = "https://example.invalid/binary"
        with self.assertRaisesRegex(installer.ProvisionError, "outside the selected"):
            self.provision()
        self.assert_untouched()

    def test_upstream_repository_asset_url_is_rejected(self):
        self.release["assets"][0]["browser_download_url"] = (
            "https://github.com/miyako/4d-form/releases/download/v0.1.0/"
            "fourdform-macos-universal.tar.xz"
        )
        with self.assertRaisesRegex(installer.ProvisionError, "selected skills release"):
            self.provision()
        self.assert_untouched()

    def test_other_architecture_asset_is_not_a_fallback(self):
        self.release["assets"][0]["name"] = "fourdform-macos-x64.tar.xz"
        with self.assertRaisesRegex(installer.ProvisionError, "exactly one release asset"):
            self.provision()
        self.assert_untouched()

    def test_missing_duplicate_assets_and_invalid_digest_are_rejected(self):
        asset = self.release["assets"].pop(0)
        with self.assertRaisesRegex(installer.ProvisionError, "exactly one release asset"):
            self.provision()
        self.release["assets"].extend([asset, asset])
        with self.assertRaisesRegex(installer.ProvisionError, "exactly one release asset"):
            self.provision()
        self.release["assets"].pop()
        asset["digest"] = "sha256:invalid"
        with self.assertRaisesRegex(installer.ProvisionError, "Unusable GitHub"):
            self.provision()
        self.assert_untouched()

    def test_wrong_path_nonexecutable_symlink_and_duplicate_binary_are_rejected(self):
        valid = ("fourdform", b"binary", 0o755, tarfile.REGTYPE)
        archives = [
            [("../fourdform", b"binary", 0o755, tarfile.REGTYPE)],
            [("fourdform", b"binary", 0o644, tarfile.REGTYPE)],
            [("fourdform", b"", 0o755, tarfile.SYMTYPE)],
            [valid, valid],
        ]
        for members in archives:
            with self.subTest(members=members):
                self.set_release(package(members))
                with self.assertRaises(installer.ProvisionError):
                    self.provision()
                self.assert_untouched()

    def test_extra_archive_paths_are_never_extracted(self):
        self.set_release(package([
            ("fourdform", b"binary", 0o755, tarfile.REGTYPE),
            ("../leaked", b"not extracted", 0o755, tarfile.REGTYPE),
        ]))
        self.provision()
        self.assertEqual(list(self.destination.parent.iterdir()), [self.destination])
        self.assertFalse((self.root / "leaked").exists())

    def test_wrong_architecture_version_and_missing_help_fail_before_install(self):
        for bad in ("architecture", "version", "help"):
            with self.subTest(bad=bad):
                def command(arguments):
                    if bad == "architecture" and arguments[0] == "lipo":
                        return "x86_64"
                    if bad == "version" and arguments[1] == "--version":
                        return "fourdform 9.9.9"
                    if bad == "help" and arguments[1] == "--help":
                        return "--output"
                    return self.command(arguments)
                self.run.side_effect = command
                with self.assertRaises(installer.ProvisionError):
                    self.provision()
                self.assertFalse(self.destination.exists())
                self.assertFalse((self.root / ".gitignore").exists())

    def test_symlinked_tools_destination_and_ignore_are_not_modified(self):
        outside = self.root / "outside"
        outside.mkdir()
        tools = self.root / "tools"
        try:
            tools.symlink_to(outside, target_is_directory=True)
        except OSError as error:
            if sys.platform == "win32" and error.winerror == 1314:
                self.skipTest("Windows symlink privilege unavailable")
            raise
        with self.assertRaisesRegex(installer.ProvisionError, "symlinked installation"):
            self.provision()
        tools.unlink()
        tools.mkdir()
        self.destination.parent.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(installer.ProvisionError, "symlinked installation"):
            self.provision()
        self.destination.parent.unlink()
        self.destination.parent.mkdir()
        other = outside / "other"
        other.write_text("retained")
        self.destination.symlink_to(other)
        with self.assertRaisesRegex(installer.ProvisionError, "symlinked installation"):
            self.provision(replace=True)
        self.destination.unlink()
        (self.root / ".gitignore").symlink_to(other)
        with self.assertRaisesRegex(installer.ProvisionError, "symlinked .gitignore"):
            self.provision()
        self.assertEqual(other.read_text(), "retained")
        self.assertFalse(self.destination.exists())


class WindowsProvisionTests(unittest.TestCase):
    mock = ProvisionTests.mock
    command = ProvisionTests.command
    set_release = ProvisionTests.set_release
    download = ProvisionTests.download
    provision = ProvisionTests.provision
    assert_untouched = ProvisionTests.assert_untouched

    def setUp(self):
        ProvisionTests.setUp(self)
        self.system.return_value = "Windows"
        self.windows_version = self.mock(
            "platform.win32_ver", return_value=("10", "10.0.22631", "", "")
        )
        self.manifest = installer.check_platform(self.manifest)
        self.destination = self.root / installer.DESTINATION.parent / "fourdform.exe"
        self.set_release(windows_package())

    def test_windows_architectures_and_aliases_select_and_install_full_package(self):
        for machine, architecture, suffix in (
            ("AMD64", "x86_64", "x64"), ("x86_64", "x86_64", "x64"),
            ("ARM64", "arm64", "arm64"), ("aarch64", "arm64", "arm64"),
        ):
            with self.subTest(machine=machine):
                self.machine.return_value = machine
                self.manifest = installer.check_platform(self.manifest)
                self.assertEqual(self.manifest["asset"], f"fourdform-windows-{suffix}.zip")
                self.set_release(windows_package(architecture))
                self.assertEqual(self.provision(replace=True), self.destination)
                self.assertEqual(self.destination.read_bytes(), pe_image(architecture))
                self.assertEqual(
                    {path.name for path in self.destination.parent.iterdir()},
                    {"fourdform.exe", "swiftCore.dll", "vcruntime140.dll", "WebView2-SDK-LICENSE.txt"},
                )
                self.assertTrue(all(call.args[0][0] != "lipo" for call in self.run.call_args_list))

    def test_old_windows_and_unknown_architecture_fail_before_download(self):
        self.windows_version.return_value = ("8", "6.3.9600", "", "")
        with self.assertRaisesRegex(installer.ProvisionError, "requires Windows 10.0"):
            self.provision()
        self.windows_version.return_value = ("10", "10.0.22631", "", "")
        self.machine.return_value = "x86"
        with self.assertRaisesRegex(installer.ProvisionError, "Unsupported Windows architecture"):
            self.provision()
        self.fetch.assert_not_called()
        self.assert_untouched()

    def test_reuses_compatible_binary_and_keeps_boon_on_replacement(self):
        self.provision()
        boon = self.destination.parent / "boon.exe"
        boon.write_bytes(b"other tool")
        self.fetch.reset_mock()
        self.provision()
        self.fetch.assert_not_called()
        self.provision(replace=True)
        self.assertEqual(boon.read_bytes(), b"other tool")
        self.assertEqual((self.root / ".gitignore").read_text(), "/tools/4dform/\n")

    def test_unicode_ignore_is_preserved(self):
        ignore = self.root / ".gitignore"
        text = "# \u30c4\u30fc\u30eb\nexisting-entry\n"
        ignore.write_text(text, encoding="utf-8")
        self.provision()
        self.assertEqual(ignore.read_text(encoding="utf-8"), text + "/tools/4dform/\n")

    def test_unsafe_incomplete_and_wrong_architecture_packages_are_rejected(self):
        valid = [
            ("fourdform.exe", pe_image()),
            ("WebView2-SDK-LICENSE.txt", b"notice"),
        ]
        for members in (
            valid[:1], valid[1:], valid + [valid[0]],
            valid + [("FOURDFORM.EXE", pe_image())],
            valid + [("../leaked.dll", pe_image())],
            valid + [("subdir/runtime.dll", pe_image())],
            valid + [("unexpected.exe", pe_image())],
            valid + [("runtime.dll", pe_image("x86_64"))],
            [("fourdform.exe", pe_image("x86_64")), valid[1]],
            [("fourdform.exe", b"not a PE image"), valid[1]],
        ):
            with self.subTest(members=members):
                self.set_release(windows_package(members=members))
                with self.assertRaises(installer.ProvisionError):
                    self.provision()
                self.assert_untouched()
                self.assertFalse((self.root / "leaked.dll").exists())

    def test_zip_symlinks_are_rejected(self):
        output = io.BytesIO(windows_package())
        with zipfile.ZipFile(output, "a") as archive:
            link = zipfile.ZipInfo("runtime.dll")
            link.create_system = 3
            link.external_attr = 0o120777 << 16
            archive.writestr(link, "../outside")
        self.set_release(output.getvalue())
        with self.assertRaisesRegex(installer.ProvisionError, "Unexpected Windows archive member"):
            self.provision()
        self.assert_untouched()

    def test_failed_replacement_rolls_back_all_companion_files(self):
        self.provision()
        original = {path.name: path.read_bytes() for path in self.destination.parent.iterdir()}
        self.set_release(windows_package(members=[
            ("fourdform.exe", pe_image()),
            ("swiftCore.dll", pe_image() + b"updated"),
            ("newRuntime.dll", pe_image()),
            ("WebView2-SDK-LICENSE.txt", b"updated notice"),
        ]))
        replace = installer.os.replace

        def fail_binary(source, target):
            if Path(source).name == "fourdform.exe" and Path(source).parent.name != "backups":
                raise OSError("fixture installation failure")
            return replace(source, target)

        with patch.object(installer.os, "replace", side_effect=fail_binary):
            with self.assertRaisesRegex(OSError, "fixture installation failure"):
                self.provision(replace=True)
        self.assertEqual(
            {path.name: path.read_bytes() for path in self.destination.parent.iterdir()}, original
        )

    def test_missing_runtime_error_is_explicit_and_does_not_install(self):
        self.run.side_effect = installer.ProvisionError("Missing Swift runtime DLL")
        with self.assertRaisesRegex(installer.ProvisionError, "Missing Swift runtime DLL"):
            self.provision()
        self.assertFalse(self.destination.exists())
        self.assertFalse((self.root / ".gitignore").exists())

    def test_local_archive_fetcher_uses_real_checksums_without_network(self):
        assets = self.root / "assets"
        assets.mkdir()
        archive = assets / self.manifest["asset"]
        archive.write_bytes(windows_package())
        sums = assets / "SHA256SUMS.arm64"
        sums.write_bytes(self.downloads[self.prefix + "SHA256SUMS"])
        fetcher = smoke.archive_fetcher(assets, self.manifest)
        installer.provision(self.root, self.manifest, fetcher=fetcher)
        self.fetch.assert_not_called()
        self.assertTrue(self.destination.is_file())
        sums.write_text("0" * 64 + "  " + self.manifest["asset"] + "\n")
        fetcher = smoke.archive_fetcher(assets, self.manifest)
        with self.assertRaisesRegex(installer.ProvisionError, "archive SHA-256 mismatch"):
            installer.provision(self.root, self.manifest, replace=True, fetcher=fetcher)


class PngVerificationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.output = Path(self.temporary.name) / "output.png"
        self.header = self.chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0))
        self.pixels = self.chunk(b"IDAT", zlib.compress(b"\x00\xff\x00\x00\xff"))
        self.ending = self.chunk(b"IEND", b"")
        self.signature = b"\x89PNG\r\n\x1a\n"

    def test_local_binary_smoke_never_provisions_or_downloads(self):
        binary = self.output.parent / "fourdform"
        binary.write_bytes(b"fixture binary")
        root = self.output.parent / "consumer"

        def rendered(binary, output, *options, **kwargs):
            if "--max-dimension" in options:
                theme = options[options.index("--theme") + 1]
                return (256, 241), theme
            if "form" in kwargs:
                form = json.loads(kwargs["form"].read_text())
                if "--theme" in options:
                    theme = options[options.index("--theme") + 1]
                else:
                    theme = "fluent-dark" if form.get("colorScheme") == "dark" else (
                        "fluent-light" if form.get("fluentUI") else "classic"
                    )
                return (440, 414), theme
            scale = int(options[options.index("--scale") + 1])
            return (440 * scale, 414 * scale), "pixels"

        def failure(arguments, **kwargs):
            return subprocess.CompletedProcess(
                [], 2 if "--theme" in arguments else 1, "", "Fixture error"
            )
        for system in ("Darwin", "Windows"):
            with self.subTest(system=system), \
                    patch.object(smoke.installer, "provision") as provision, \
                    patch.object(smoke.installer, "verify_binary") as verify, \
                    patch.object(smoke.installer, "check_platform", return_value={}), \
                    patch.object(smoke.platform, "system", return_value=system), \
                    patch.object(smoke, "render", side_effect=rendered), \
                    patch.object(smoke.subprocess, "run", side_effect=failure):
                smoke.smoke(root / system, binary)
                provision.assert_not_called()
                verify.assert_called_once_with(binary, {})
                self.assertFalse((root / system / ".gitignore").exists())

    def chunk(self, kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    def test_accepts_actual_png_with_valid_crc_and_decompressed_pixels(self):
        self.output.write_bytes(self.signature + self.header + self.pixels + self.ending)
        dimensions, pixels = smoke.png_info(self.output)
        self.assertEqual(dimensions, (1, 1))
        self.assertEqual(pixels, hashlib.sha256(b"\x00\xff\x00\x00\xff").hexdigest())

    def test_rejects_html_even_with_png_filename(self):
        self.output.write_bytes(b"<html>not an image</html>")
        with self.assertRaisesRegex(smoke.SmokeError, "not PNG"):
            smoke.png_info(self.output)

    def test_rejects_truncated_corrupt_or_incomplete_png(self):
        valid = self.signature + self.header + self.pixels + self.ending
        for data in (
            valid[:-1], valid[:8] + b"\x00", self.signature + self.header + self.ending,
            self.signature + self.header + self.pixels,
            valid[:-4] + b"\x00\x00\x00\x00", valid + b"trailing",
        ):
            with self.subTest(data=data):
                self.output.write_bytes(data)
                with self.assertRaises(smoke.SmokeError):
                    smoke.png_info(self.output)

    def test_rejects_invalid_compressed_pixels_and_zero_dimensions(self):
        empty = self.chunk(b"IHDR", struct.pack(">IIBBBBB", 0, 1, 8, 6, 0, 0, 0))
        self.output.write_bytes(self.signature + empty + self.pixels + self.ending)
        with self.assertRaisesRegex(smoke.SmokeError, "empty PNG dimensions"):
            smoke.png_info(self.output)
        truncated = self.chunk(b"IDAT", zlib.compress(b"\x00\xff\x00\x00\xff")[:-2])
        self.output.write_bytes(self.signature + self.header + truncated + self.ending)
        with self.assertRaisesRegex(smoke.SmokeError, "invalid PNG pixels"):
            smoke.png_info(self.output)

    def test_rejects_wrong_raster_shape_and_invalid_scanline_filter(self):
        for raster, error in ((b"not a 1x1 raster", "raster dimensions"),
                              (b"\x05\xff\x00\x00\xff", "scanline filter")):
            with self.subTest(raster=raster):
                invalid = self.chunk(b"IDAT", zlib.compress(raster))
                self.output.write_bytes(self.signature + self.header + invalid + self.ending)
                with self.assertRaisesRegex(smoke.SmokeError, error):
                    smoke.png_info(self.output)


if __name__ == "__main__":
    unittest.main()
