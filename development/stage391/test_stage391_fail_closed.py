#!/usr/bin/env python3

import copy
import importlib.util
import json
import tempfile
from pathlib import Path


VERIFIER_PATH = Path(
    "development/stage391/"
    "verify_stage391_third_party_submission.py"
)


def load_verifier():
    spec = importlib.util.spec_from_file_location(
        "stage391_verifier",
        VERIFIER_PATH,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            "unable to load Stage391 verifier"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    spec.loader.exec_module(
        module
    )

    return module


VERIFIER = load_verifier()


def base_submission():
    return {
        "schema":
            "qsp.stage390."
            "assessment-submission-schema.v1",

        "stage":
            390,

        "submission_origin":
            "independent_third_party",

        "assessor": {
            "assessor_id":
                "independent-assessor-example",

            "independence_declared":
                True,
        },

        "environment": {
            "os":
                "Linux",

            "os_version":
                "test",

            "architecture":
                "x86_64",

            "python_version":
                "3.12",

            "openssl_version":
                "test",

            "execution_mode":
                "offline",
        },

        "upstream_binding": {
            "stage389_result_sha256":
                "3a8815593fd4b570b881e39806c57e32"
                "f11d7aec7f544e30481021167b2667c4",

            "stage389_commit":
                "65c881d6c4a27cc9d49726c998b2fc"
                "96de48b117",
        },

        "reproduction": {
            "reproduction_completed":
                True,

            "deterministic_result_obtained":
                True,

            "reference_result_compared":
                True,

            "critical_mismatch_count":
                0,
        },

        "assessment": {
            "outcome":
                "agreement",

            "findings":
                [],
        },
    }


def assert_rejected(
    data,
    expected_failure,
):
    result = VERIFIER.validate_submission(
        data
    )

    assert (
        result["decision"]
        == "third_party_submission_rejected"
    ), result

    assert (
        result["external_assessment_completed"]
        is False
    ), result

    assert (
        result["verified_third_party_agreement"]
        is False
    ), result

    assert (
        result["stage389_dual_timestamp_verified"]
        is False
    ), result

    assert (
        expected_failure
        in result["failures"]
    ), result


def test_f01_self_test_rejected():
    data = base_submission()
    data["submission_origin"] = "self_test"

    assert_rejected(
        data,
        "submission_origin_not_independent_third_party",
    )

    print(
        "PASS: F01 self-test cannot qualify as external assessment"
    )


def test_f02_smoke_test_rejected():
    data = base_submission()
    data["submission_origin"] = "smoke_test"

    assert_rejected(
        data,
        "submission_origin_not_independent_third_party",
    )

    print(
        "PASS: F02 smoke-test cannot qualify as external assessment"
    )


def test_f03_missing_independence_rejected():
    data = base_submission()
    data["assessor"][
        "independence_declared"
    ] = False

    assert_rejected(
        data,
        "independence_declaration_missing_or_false",
    )

    print(
        "PASS: F03 missing independence declaration rejected"
    )


def test_f04_stage389_sha_tamper():
    data = base_submission()

    data["upstream_binding"][
        "stage389_result_sha256"
    ] = "0" * 64

    assert_rejected(
        data,
        "stage389_result_sha_binding_mismatch",
    )

    print(
        "PASS: F04 Stage389 result SHA tampering rejected"
    )


def test_f05_stage389_commit_tamper():
    data = base_submission()

    data["upstream_binding"][
        "stage389_commit"
    ] = "0" * 40

    assert_rejected(
        data,
        "stage389_commit_binding_mismatch",
    )

    print(
        "PASS: F05 Stage389 commit tampering rejected"
    )


def test_f06_agreement_with_mismatch():
    data = base_submission()

    data["reproduction"][
        "critical_mismatch_count"
    ] = 1

    assert_rejected(
        data,
        "agreement_requires_zero_mismatch",
    )

    print(
        "PASS: F06 agreement with mismatch rejected"
    )


def test_f07_disagreement_without_mismatch():
    data = base_submission()

    data["assessment"][
        "outcome"
    ] = "disagreement"

    data["reproduction"][
        "critical_mismatch_count"
    ] = 0

    assert_rejected(
        data,
        "disagreement_requires_positive_mismatch",
    )

    print(
        "PASS: F07 disagreement with zero mismatch rejected"
    )


def test_f08_incomplete_but_completed():
    data = base_submission()

    data["assessment"][
        "outcome"
    ] = "incomplete"

    data["reproduction"][
        "reproduction_completed"
    ] = True

    assert_rejected(
        data,
        "incomplete_requires_reproduction_completed_false",
    )

    print(
        "PASS: F08 incomplete with completed reproduction rejected"
    )


def test_f09_negative_mismatch():
    data = base_submission()

    data["reproduction"][
        "critical_mismatch_count"
    ] = -1

    assert_rejected(
        data,
        "critical_mismatch_count_invalid",
    )

    print(
        "PASS: F09 negative mismatch count rejected"
    )


def test_f10_boolean_mismatch():
    data = base_submission()

    data["reproduction"][
        "critical_mismatch_count"
    ] = True

    assert_rejected(
        data,
        "critical_mismatch_count_invalid",
    )

    print(
        "PASS: F10 Boolean mismatch count rejected"
    )


def test_f11_forbidden_external_claim():
    data = base_submission()

    data[
        "external_assessment_completed"
    ] = True

    assert_rejected(
        data,
        "forbidden_self_assertion:"
        "external_assessment_completed",
    )

    print(
        "PASS: F11 forged external assessment completion rejected"
    )


def test_f12_forbidden_certification_claim():
    data = base_submission()

    data[
        "formal_certification"
    ] = True

    assert_rejected(
        data,
        "forbidden_self_assertion:"
        "formal_certification",
    )

    print(
        "PASS: F12 forged formal certification rejected"
    )


def test_f13_stage389_timestamp_promotion():
    data = base_submission()

    data[
        "stage389_dual_timestamp_verified"
    ] = True

    assert_rejected(
        data,
        "forbidden_self_assertion:"
        "stage389_dual_timestamp_verified",
    )

    print(
        "PASS: F13 Stage389 timestamp self-promotion rejected"
    )


def test_f14_missing_required_field():
    data = base_submission()

    del data["assessment"]

    result = VERIFIER.validate_submission(
        data
    )

    assert (
        result["decision"]
        == "third_party_submission_rejected"
    ), result

    assert any(
        failure
        == "submission.assessment"
        for failure in result["failures"]
    ), result

    print(
        "PASS: F14 missing required field rejected"
    )


def test_f15_invalid_execution_mode():
    data = base_submission()

    data["environment"][
        "execution_mode"
    ] = "unknown-mode"

    assert_rejected(
        data,
        "execution_mode_invalid",
    )

    print(
        "PASS: F15 invalid execution mode rejected"
    )


def test_f16_malformed_json():
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".json",
        delete=False,
    ) as handle:
        handle.write(
            "{malformed"
        )

        path = Path(
            handle.name
        )

    try:
        try:
            VERIFIER.load_json(
                path
            )

        except json.JSONDecodeError:
            print(
                "PASS: F16 malformed JSON rejected"
            )

        else:
            raise AssertionError(
                "malformed JSON was accepted"
            )

    finally:
        path.unlink(
            missing_ok=True
        )


def test_f17_valid_agreement_fixture():
    data = base_submission()

    result = VERIFIER.validate_submission(
        data
    )

    assert (
        result["decision"]
        == "third_party_reproduction_agreement_verified"
    ), result

    assert (
        result["assessment_outcome"]
        == "agreement"
    ), result

    assert (
        result["verified_third_party_agreement"]
        is True
    ), result

    assert (
        result["external_assessment_completed"]
        is True
    ), result

    assert (
        result["stage389_dual_timestamp_verified"]
        is False
    ), result

    print(
        "PASS: P01 valid independent agreement fixture classified correctly"
    )


def test_f18_valid_disagreement_fixture():
    data = base_submission()

    data["assessment"][
        "outcome"
    ] = "disagreement"

    data["reproduction"][
        "critical_mismatch_count"
    ] = 2

    result = VERIFIER.validate_submission(
        data
    )

    assert (
        result["decision"]
        == "third_party_reproduction_disagreement_verified"
    ), result

    assert (
        result["assessment_outcome"]
        == "disagreement"
    ), result

    assert (
        result["verified_third_party_disagreement"]
        is True
    ), result

    assert (
        result["stage389_dual_timestamp_verified"]
        is False
    ), result

    print(
        "PASS: P02 valid disagreement fixture classified correctly"
    )


def test_f19_valid_incomplete_fixture():
    data = base_submission()

    data["assessment"][
        "outcome"
    ] = "incomplete"

    data["reproduction"][
        "reproduction_completed"
    ] = False

    data["reproduction"][
        "deterministic_result_obtained"
    ] = False

    data["reproduction"][
        "reference_result_compared"
    ] = False

    result = VERIFIER.validate_submission(
        data
    )

    assert (
        result["decision"]
        == "third_party_reproduction_incomplete"
    ), result

    assert (
        result["assessment_outcome"]
        == "incomplete"
    ), result

    assert (
        result["external_assessment_completed"]
        is False
    ), result

    assert (
        result["stage389_dual_timestamp_verified"]
        is False
    ), result

    print(
        "PASS: P03 valid incomplete fixture classified correctly"
    )


def main():
    negative_tests = [
        test_f01_self_test_rejected,
        test_f02_smoke_test_rejected,
        test_f03_missing_independence_rejected,
        test_f04_stage389_sha_tamper,
        test_f05_stage389_commit_tamper,
        test_f06_agreement_with_mismatch,
        test_f07_disagreement_without_mismatch,
        test_f08_incomplete_but_completed,
        test_f09_negative_mismatch,
        test_f10_boolean_mismatch,
        test_f11_forbidden_external_claim,
        test_f12_forbidden_certification_claim,
        test_f13_stage389_timestamp_promotion,
        test_f14_missing_required_field,
        test_f15_invalid_execution_mode,
        test_f16_malformed_json,
    ]

    positive_classification_tests = [
        test_f17_valid_agreement_fixture,
        test_f18_valid_disagreement_fixture,
        test_f19_valid_incomplete_fixture,
    ]

    for test in negative_tests:
        test()

    for test in positive_classification_tests:
        test()

    print()
    print(
        "PASS: all Stage391 Fail-Closed "
        "regression tests passed"
    )

    print(
        "total_negative_tests =",
        len(negative_tests),
    )

    print(
        "total_positive_classification_tests =",
        len(
            positive_classification_tests
        ),
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
