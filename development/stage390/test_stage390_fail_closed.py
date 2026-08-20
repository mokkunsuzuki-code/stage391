#!/usr/bin/env python3

import copy
import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

VERIFIER = (
    ROOT
    / "development"
    / "stage390"
    / "verify_stage390_assessment_intake.py"
)

EXPECTED_SHA = (
    "3a8815593fd4b570b881e39806c57e32"
    "f11d7aec7f544e30481021167b2667c4"
)

EXPECTED_COMMIT = (
    "65c881d6c4a27cc9d49726c998b2fc96"
    "de48b117"
)


def base_submission():
    return {
        "schema":
            "qsp.stage390.assessment-submission.v1",
        "stage":
            390,
        "assessor": {
            "assessor_id":
                "stage390-negative-test",
            "independence_declared":
                True,
        },
        "environment": {
            "os":
                "test",
            "os_version":
                "test",
            "architecture":
                "test",
            "python_version":
                "test",
            "openssl_version":
                "test",
            "execution_mode":
                "offline",
        },
        "upstream_binding": {
            "stage389_result_sha256":
                EXPECTED_SHA,
            "stage389_commit":
                EXPECTED_COMMIT,
        },
        "reproduction": {
            "upstream_binding_verified":
                True,
            "evidence_hash_integrity_verified":
                True,
            "deterministic_verification_completed":
                True,
            "fail_closed_behavior_verified":
                True,
            "publication_boundary_verified":
                True,
            "critical_mismatch_count":
                0,
            "reproduction_completed":
                True,
        },
        "assessment": {
            "outcome":
                "agreement",
            "findings":
                [],
        },
    }


def execute_submission(data):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "submission.json"

        path.write_text(
            json.dumps(
                data,
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

        completed = subprocess.run(
            [
                "python3",
                str(VERIFIER),
                "--submission",
                str(path),
            ],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        result = json.loads(
            completed.stdout
        )

        return (
            completed.returncode,
            result,
        )


def execute_raw(text):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "submission.json"

        path.write_text(
            text,
            encoding="utf-8",
        )

        completed = subprocess.run(
            [
                "python3",
                str(VERIFIER),
                "--submission",
                str(path),
            ],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        result = json.loads(
            completed.stdout
        )

        return (
            completed.returncode,
            result,
        )


def require_fail_closed(
    name,
    data=None,
    raw_text=None,
):
    if raw_text is not None:
        code, result = execute_raw(
            raw_text
        )
    else:
        code, result = execute_submission(
            data
        )

    assert code != 0, (
        name
        + ": verifier unexpectedly succeeded"
    )

    assert (
        result["decision"]
        == "fail_closed"
    ), (
        name
        + ": decision was not fail_closed"
    )

    assert (
        result["critical_failure_count"]
        >= 1
    ), (
        name
        + ": no critical failure recorded"
    )

    assert (
        result["external_assessment_completed"]
        is False
    )

    assert (
        result["formal_certification"]
        is False
    )

    assert (
        result["system_wide_formal_acceptance"]
        is False
    )

    assert (
        result["entire_system_quantum_safe"]
        is False
    )

    assert (
        result["stage389_dual_timestamp_verified"]
        is False
    )

    print(
        "PASS:",
        name,
    )


def test_f01():
    d = base_submission()
    d[
        "external_assessment_completed"
    ] = True

    require_fail_closed(
        "F01 forged external assessment completion rejected",
        d,
    )


def test_f02():
    d = base_submission()
    d[
        "formal_certification"
    ] = True

    require_fail_closed(
        "F02 forged formal certification rejected",
        d,
    )


def test_f03():
    d = base_submission()
    d[
        "upstream_binding"
    ][
        "stage389_result_sha256"
    ] = "0" * 64

    require_fail_closed(
        "F03 Stage389 result SHA tampering rejected",
        d,
    )


def test_f04():
    d = base_submission()
    d[
        "upstream_binding"
    ][
        "stage389_commit"
    ] = "0" * 40

    require_fail_closed(
        "F04 Stage389 commit tampering rejected",
        d,
    )


def test_f05():
    d = base_submission()
    d[
        "assessor"
    ][
        "independence_declared"
    ] = False

    require_fail_closed(
        "F05 missing independence declaration rejected",
        d,
    )


def test_f06():
    d = base_submission()
    d[
        "environment"
    ][
        "execution_mode"
    ] = "invalid-mode"

    require_fail_closed(
        "F06 invalid execution mode rejected",
        d,
    )


def test_f07():
    d = base_submission()

    d[
        "reproduction"
    ][
        "reproduction_completed"
    ] = False

    d[
        "assessment"
    ][
        "outcome"
    ] = "agreement"

    require_fail_closed(
        "F07 incomplete reproduction cannot claim agreement",
        d,
    )


def test_f08():
    d = base_submission()

    d[
        "assessment"
    ][
        "outcome"
    ] = "disagreement"

    require_fail_closed(
        "F08 zero-mismatch result cannot claim disagreement",
        d,
    )


def test_f09():
    d = base_submission()

    d[
        "reproduction"
    ][
        "critical_mismatch_count"
    ] = -1

    require_fail_closed(
        "F09 negative mismatch count rejected",
        d,
    )


def test_f10():
    d = base_submission()

    d[
        "reproduction"
    ][
        "critical_mismatch_count"
    ] = True

    require_fail_closed(
        "F10 Boolean mismatch count rejected",
        d,
    )


def test_f11():
    d = base_submission()

    del d[
        "environment"
    ][
        "openssl_version"
    ]

    require_fail_closed(
        "F11 missing required field rejected",
        d,
    )


def test_f12():
    require_fail_closed(
        "F12 malformed JSON rejected",
        raw_text="{not-valid-json",
    )


def main():
    tests = [
        test_f01,
        test_f02,
        test_f03,
        test_f04,
        test_f05,
        test_f06,
        test_f07,
        test_f08,
        test_f09,
        test_f10,
        test_f11,
        test_f12,
    ]

    for test in tests:
        test()

    print()
    print(
        "PASS: all Stage390 Fail-Closed "
        "regression tests passed"
    )

    print(
        "total_negative_tests =",
        len(tests),
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
