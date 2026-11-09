#!/usr/bin/env python3
"""Submit once, then poll the same Apple notarization submission with a deadline."""

import argparse
import json
import os
import subprocess
import sys
import time
import uuid


POLL_TIMEOUT = 1200
POLL_INTERVAL = 15
REQUEST_TIMEOUT = 120
SUBMIT_TIMEOUT = 300


class NotarizationError(Exception):
    pass


def report(message):
    # Do not expose credentials even if notarytool includes them in an error.
    for name in ("APPLE_ID", "APPLE_PASSWORD", "TEAM_ID"):
        value = os.environ.get(name)
        if value:
            message = message.replace(value, "***")
    print(message, flush=True)


def command(action, argument, credentials, timeout):
    return subprocess.run(
        ["xcrun", "notarytool", action, argument, *credentials,
         "--output-format", "json", "--no-progress"],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def response(output):
    try:
        result = json.loads(output)
    except json.JSONDecodeError as error:
        raise NotarizationError("notarytool returned invalid JSON") from error
    if not isinstance(result, dict):
        raise NotarizationError("notarytool returned a non-object response")
    return result


def submission_id(value):
    try:
        return str(uuid.UUID(value))
    except (ValueError, TypeError, AttributeError) as error:
        raise NotarizationError("notarytool submission ID must be a UUID") from error


def rejection_log(identifier, credentials):
    try:
        result = command("log", identifier, credentials, 60)
    except subprocess.TimeoutExpired:
        report(f"Could not retrieve rejection log for {identifier}: request timed out")
        return
    report(result.stdout)
    if result.returncode:
        report(f"Could not retrieve rejection log (exit {result.returncode}): {result.stderr}")


def notarize(archive=None, identifier=None):
    credentials = []
    for name, flag in (
        ("APPLE_ID", "--apple-id"),
        ("APPLE_PASSWORD", "--password"),
        ("TEAM_ID", "--team-id"),
    ):
        value = os.environ.get(name)
        if not value:
            raise NotarizationError(f"Missing required environment variable: {name}")
        credentials.extend((flag, value))

    if identifier is None:
        try:
            result = command("submit", archive, credentials, SUBMIT_TIMEOUT)
        except subprocess.TimeoutExpired as error:
            raise NotarizationError(
                "Submission request timed out; upload outcome is unknown. "
                "Check notarytool history before resubmitting."
            ) from error
        if result.returncode:
            report(result.stdout)
            report(result.stderr)
            raise NotarizationError(
                f"Submission failed (exit {result.returncode}); not resubmitting automatically"
            )
        identifier = submission_id(response(result.stdout).get("id"))
    else:
        identifier = submission_id(identifier)

    report(f"Notarization submission ID: {identifier}")
    deadline = time.monotonic() + POLL_TIMEOUT
    while time.monotonic() < deadline:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        try:
            result = command("info", identifier, credentials, min(REQUEST_TIMEOUT, remaining))
        except subprocess.TimeoutExpired:
            report(f"Status request timed out for {identifier}; retrying the same submission")
        else:
            if result.returncode:
                report(
                    f"Status request failed for {identifier} (exit {result.returncode}); "
                    f"retrying the same submission: {result.stderr}"
                )
            else:
                status = response(result.stdout).get("status")
                report(f"Notarization status for {identifier}: {status}")
                if status == "Accepted":
                    return
                if status in ("Invalid", "Rejected"):
                    rejection_log(identifier, credentials)
                    raise NotarizationError(f"Notarization {status}: {identifier}")
                if status != "In Progress":
                    raise NotarizationError(
                        f"Unexpected notarization status for {identifier}: {status!r}"
                    )
        remaining = deadline - time.monotonic()
        if remaining > 0:
            time.sleep(min(POLL_INTERVAL, remaining))

    raise NotarizationError(
        f"Notarization did not complete within {POLL_TIMEOUT}s: {identifier}. "
        f"Resume with: python3 .github/scripts/notarize.py --submission-id {identifier}"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--archive", help="Signed ZIP to submit once")
    source.add_argument("--submission-id", help="Resume polling an existing submission")
    args = parser.parse_args()
    try:
        notarize(args.archive, args.submission_id)
    except (NotarizationError, OSError) as error:
        report(f"Notarization failed: {error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
