#!/usr/bin/env python3
"""Offline regression tests for release notarization and workflow wiring."""

import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).with_name("notarize.py")
SPEC = importlib.util.spec_from_file_location("notarize", SCRIPT)
notary = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(notary)
IDENTIFIER = "4031aed1-5bfd-473c-8ecd-e8804b05b59f"
ENVIRONMENT = {
    "APPLE_ID": "fixture@example.test",
    "APPLE_PASSWORD": "fixture-app-password",
    "TEAM_ID": "FIXTURETEAM",
}


def result(data=None, code=0, stderr=""):
    return subprocess.CompletedProcess(
        [], code, json.dumps(data if data is not None else {"id": IDENTIFIER}), stderr
    )


def status(value):
    return result({"id": IDENTIFIER, "status": value})


class NotarizeTests(unittest.TestCase):
    def setUp(self):
        self.now = 0
        self.output = io.StringIO()
        self.enterContext(contextlib.redirect_stdout(self.output))
        self.enterContext(patch.dict(os.environ, ENVIRONMENT, clear=True))
        self.run = self.enterContext(patch.object(notary.subprocess, "run"))
        self.enterContext(patch.object(notary.time, "monotonic", side_effect=lambda: self.now))
        self.sleep = self.enterContext(patch.object(notary.time, "sleep", side_effect=self.advance))

    # Keep these tests runnable on the Python 3.9 used by release CI checks.
    def enterContext(self, manager):
        value = manager.__enter__()
        self.addCleanup(manager.__exit__, None, None, None)
        return value

    def advance(self, seconds):
        self.now += seconds

    def actions(self):
        return [call.args[0][2] for call in self.run.call_args_list]

    def assert_single_submission(self):
        self.assertEqual(self.actions().count("submit"), 1)
        for call in self.run.call_args_list:
            argv = call.args[0]
            self.assertNotIn("--wait", argv)
            self.assertEqual(argv[-3:], ["--output-format", "json", "--no-progress"])
            if argv[2] == "info":
                self.assertEqual(argv[3], IDENTIFIER)
                self.assertLessEqual(call.kwargs["timeout"], notary.REQUEST_TIMEOUT)

    def test_submit_once_and_accept_after_in_progress(self):
        self.run.side_effect = [result(), status("In Progress"), status("Accepted")]
        notary.notarize("signed.zip")
        self.assertEqual(self.actions(), ["submit", "info", "info"])
        self.assertEqual(self.run.call_args_list[0].args[0][3], "signed.zip")
        self.assertEqual(self.run.call_args_list[0].kwargs["timeout"], 300)
        self.assertEqual(self.now, 15)
        self.assert_single_submission()
        self.assertIn(IDENTIFIER, self.output.getvalue())

    def test_original_http_timeout_recovers_without_resubmitting(self):
        self.run.side_effect = [
            result(),
            status("In Progress"),
            result(code=1, stderr="NSURLErrorDomain Code=-1001: The request timed out."),
            status("Accepted"),
        ]
        notary.notarize("signed.zip")
        self.assert_single_submission()
        self.assertEqual(self.now, 30)
        self.assertIn("Code=-1001", self.output.getvalue())

    def test_hung_status_process_recovers(self):
        self.run.side_effect = [
            result(), subprocess.TimeoutExpired(["xcrun"], 120), status("Accepted")
        ]
        notary.notarize("signed.zip")
        self.assert_single_submission()
        self.assertIn("Status request timed out", self.output.getvalue())

    def test_terminal_rejection_is_not_retried(self):
        for terminal in ("Invalid", "Rejected"):
            with self.subTest(status=terminal):
                self.run.reset_mock()
                self.run.side_effect = [result(), status(terminal), result({"issues": ["unsigned"]})]
                with self.assertRaisesRegex(notary.NotarizationError, terminal):
                    notary.notarize("signed.zip")
                self.assertEqual(self.actions(), ["submit", "info", "log"])
                self.assertIn("unsigned", self.output.getvalue())
        self.sleep.assert_not_called()

    def test_rejection_remains_failure_if_log_request_fails(self):
        for diagnostic in (
            result(code=1, stderr="log unavailable"),
            subprocess.TimeoutExpired(["xcrun"], 60),
        ):
            with self.subTest(diagnostic=type(diagnostic).__name__):
                self.run.side_effect = [result(), status("Invalid"), diagnostic]
                with self.assertRaisesRegex(notary.NotarizationError, "Notarization Invalid"):
                    notary.notarize("signed.zip")
        self.assertIn("Could not retrieve rejection log", self.output.getvalue())

    def test_unknown_or_missing_status_never_succeeds(self):
        for value in (None, "Pending", "accepted"):
            with self.subTest(status=value):
                self.run.side_effect = [result(), status(value)]
                with self.assertRaisesRegex(notary.NotarizationError, "Unexpected"):
                    notary.notarize("signed.zip")
        self.sleep.assert_not_called()

    def test_malformed_info_response_fails_explicitly(self):
        for output in ("not JSON", "[]"):
            with self.subTest(output=output):
                self.run.side_effect = [
                    result(), subprocess.CompletedProcess([], 0, output, "")
                ]
                with self.assertRaisesRegex(notary.NotarizationError, "response|JSON"):
                    notary.notarize("signed.zip")

    def test_repeated_status_errors_and_pending_are_bounded(self):
        for pending in (status("In Progress"), result(code=1, stderr="HTTP 503")):
            with self.subTest(pending=pending.returncode):
                self.now = 0
                self.run.reset_mock()
                self.run.side_effect = None
                self.run.return_value = pending
                with self.assertRaisesRegex(notary.NotarizationError, "within 1200s") as error:
                    notary.notarize(identifier=IDENTIFIER)
                self.assertIn(f"--submission-id {IDENTIFIER}", str(error.exception))
                self.assertEqual(self.now, 1200)
                self.assertEqual(len(self.run.call_args_list), 80)
                self.assertEqual(set(self.actions()), {"info"})

    def test_request_timeout_is_clipped_to_remaining_deadline(self):
        def hung(*args, **kwargs):
            self.advance(kwargs["timeout"])
            raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])

        self.run.side_effect = hung
        with patch.object(notary, "POLL_TIMEOUT", 140):
            with self.assertRaisesRegex(notary.NotarizationError, "within 140s"):
                notary.notarize(identifier=IDENTIFIER)
        self.assertEqual(self.now, 140)
        self.assertEqual(
            [call.kwargs["timeout"] for call in self.run.call_args_list], [120, 5]
        )

    def test_resume_never_uploads(self):
        self.run.return_value = status("Accepted")
        notary.notarize(identifier=IDENTIFIER)
        self.assertEqual(self.actions(), ["info"])

    def test_failed_or_uncertain_upload_is_not_retried(self):
        for failure, message in (
            (result(code=1, stderr="upload failed"), "not resubmitting"),
            (subprocess.TimeoutExpired(["xcrun"], 300), "outcome is unknown"),
        ):
            with self.subTest(message=message):
                self.run.reset_mock()
                self.run.side_effect = [failure]
                with self.assertRaisesRegex(notary.NotarizationError, message):
                    notary.notarize("signed.zip")
                self.assertEqual(self.actions(), ["submit"])

    def test_invalid_submission_id_never_polls(self):
        for identifier in (None, "", "not-a-uuid"):
            with self.subTest(identifier=identifier):
                self.run.reset_mock()
                self.run.return_value = result({"id": identifier})
                with self.assertRaisesRegex(notary.NotarizationError, "UUID"):
                    notary.notarize("signed.zip")
                self.assertEqual(self.actions(), ["submit"])

    def test_missing_credentials_never_runs_notarytool(self):
        for name in ENVIRONMENT:
            with self.subTest(name=name), patch.dict(os.environ, {name: ""}):
                with self.assertRaisesRegex(notary.NotarizationError, name):
                    notary.notarize("signed.zip")
        self.run.assert_not_called()

    def test_diagnostics_redact_credentials(self):
        secrets = " ".join(ENVIRONMENT.values())
        self.run.side_effect = [
            result(), result(code=1, stderr=secrets), status("Invalid"),
            result({"issues": [secrets]}),
        ]
        with self.assertRaises(notary.NotarizationError):
            notary.notarize("signed.zip")
        for value in ENVIRONMENT.values():
            self.assertNotIn(value, self.output.getvalue())
        self.assertIn("***", self.output.getvalue())

    def test_cli_failure_has_nonzero_exit_without_command_or_secrets(self):
        self.run.side_effect = subprocess.TimeoutExpired(["xcrun", *ENVIRONMENT.values()], 300)
        with patch.object(sys, "argv", [str(SCRIPT), "--archive", "signed.zip"]):
            self.assertEqual(notary.main(), 1)
        for value in ENVIRONMENT.values():
            self.assertNotIn(value, self.output.getvalue())

    def test_cli_resume_and_success_exit(self):
        self.run.return_value = status("Accepted")
        with patch.object(sys, "argv", [str(SCRIPT), "--submission-id", IDENTIFIER]):
            self.assertEqual(notary.main(), 0)
        self.assertEqual(self.actions(), ["info"])

    def test_all_release_notarization_steps_use_helper(self):
        workflow = SCRIPT.parents[1] / "workflows/release.yml"
        text = workflow.read_text()
        self.assertEqual(text.count("- name: Notarize "), 9)
        self.assertEqual(
            text.count('python3 .github/scripts/notarize.py --archive "$ZIP_FILE"'), 9
        )
        self.assertNotIn("xcrun notarytool", text)
        self.assertNotIn("notarization.json", text)


if __name__ == "__main__":
    unittest.main()
