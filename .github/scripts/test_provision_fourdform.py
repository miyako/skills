#!/usr/bin/env python3
"""Offline regression tests for the consumer-side fourdform provisioner."""

import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[2] / (
    "4d-skills/skills/4dtools/scripts/provision_fourdform.py"
)
sys.dont_write_bytecode = True
SPEC = importlib.util.spec_from_file_location("provision_fourdform", SCRIPT)
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


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


class ProvisionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.manifest = installer.load_manifest(installer.MANIFEST)
        self.destination = self.root / installer.DESTINATION
        self.metadata_url = (
            f"https://api.github.com/repos/{self.manifest['repository']}/releases/tags/"
            f"{self.manifest['release_tag']}"
        )
        self.prefix = (
            f"https://github.com/{self.manifest['repository']}/releases/download/"
            f"{self.manifest['release_tag']}/"
        )
        self.system = self.mock("platform.system", return_value="Darwin")
        self.machine = self.mock("platform.machine", return_value="arm64")
        self.mac_version = self.mock("platform.mac_ver", return_value=("12.0", (), ""))
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
            return "x86_64 arm64"
        if arguments[1] == "--version":
            return "fourdform 0.1.0"
        return "--output --theme --page --scale --max-dimension --language"

    def set_release(self, archive):
        checksum = hashlib.sha256(archive).hexdigest()
        sums = f"{checksum}  {self.manifest['asset']}\n".encode()
        manifest_data = json.dumps(self.manifest["source"]).encode()
        self.release = {"tag_name": "v0.1.0", "draft": False, "assets": [
            {"name": name, "browser_download_url": self.prefix + name,
             "digest": "sha256:" + hashlib.sha256(data).hexdigest()}
            for name, data in (
                (self.manifest["asset"], archive), ("SHA256SUMS", sums),
                ("release.json", manifest_data)
            )
        ]}
        self.downloads = {
            self.prefix + self.manifest["asset"]: archive,
            self.prefix + "SHA256SUMS": sums,
            self.prefix + "release.json": manifest_data,
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
        self.assertEqual(self.destination.stat().st_mode & 0o777, 0o755)
        self.assertEqual((self.root / ".gitignore").read_text(), "existing-entry\n/tools/4dform/\n")
        self.assertEqual(script.read_text(), "echo project\n")
        self.assertEqual(self.fetch.call_count, 4)

    def test_both_macos_architectures_use_same_universal_archive(self):
        for machine in ("arm64", "x86_64"):
            with self.subTest(machine=machine):
                self.machine.return_value = machine
                self.provision(replace=True)
                self.assertEqual(self.fetch.call_args[0][0], self.prefix + self.manifest["asset"])

    def test_windows_and_linux_fail_before_download_with_no_fake_binary(self):
        for system in ("Windows", "Linux"):
            with self.subTest(system=system):
                self.system.return_value = system
                with self.assertRaises(installer.ProvisionError) as raised:
                    self.provision()
                self.assertIn("unavailable", str(raised.exception))
                if system == "Windows":
                    self.assertIn(self.manifest["windows_handover"], str(raised.exception))
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

    def test_missing_or_changed_upstream_manifest_is_rejected(self):
        asset = self.release["assets"].pop()
        with self.assertRaisesRegex(installer.ProvisionError, "release.json"):
            self.provision()
        self.release["assets"].append(asset)
        asset["digest"] = None
        source = dict(self.manifest["source"], version="9.9.9")
        self.downloads[self.prefix + "release.json"] = json.dumps(source).encode()
        with self.assertRaisesRegex(installer.ProvisionError, "differs from the committed"):
            self.provision()
        self.assert_untouched()

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
        for field, value in (("tag_name", "v9.9.9"), ("draft", True)):
            with self.subTest(field=field):
                original = self.release[field]
                self.release[field] = value
                with self.assertRaisesRegex(installer.ProvisionError, "pinned published tag"):
                    self.provision()
                self.release[field] = original
        self.release["assets"][0]["browser_download_url"] = "https://example.invalid/binary"
        with self.assertRaisesRegex(installer.ProvisionError, "outside the pinned"):
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

    def test_nonuniversal_wrong_version_and_missing_help_fail_before_install(self):
        for bad in ("architecture", "version", "help"):
            with self.subTest(bad=bad):
                def command(arguments):
                    if bad == "architecture" and arguments[0] == "lipo":
                        return "arm64"
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
        tools.symlink_to(outside, target_is_directory=True)
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


if __name__ == "__main__":
    unittest.main()
