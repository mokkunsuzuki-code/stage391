#!/usr/bin/env python3

import argparse
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

STAGE390_DIR = (
    ROOT
    / "development"
    / "stage390"
)

STAGE389_RESULT = (
    ROOT
    / "development"
    / "stage389"
    / "stage389_dual_timestamp_result.json"
)

UPSTREAM_STATE = (
    STAGE390_DIR
    / "stage390_upstream_state.json"
)

ASSESSMENT_CONTRACT = (
    STAGE390_DIR
    / "stage390_assessment_contract.json"
)

SUBMISSION_SCHEMA = (
    STAGE390_DIR
    / "stage390_assessment_submission_schema.json"
)

ENVIRONMENT_SCHEMA = (
    STAGE390_DIR
    / "stage390_assessor_environment_schema.json"
)

REPRODUCTION_SCHEMA = (
    STAGE390_DIR
    / "stage390_reproduction_result_schema.json"
)

INTAKE_POLICY = (
    STAGE390_DIR
    / "stage390_assessment_intake_policy.json"
)


def read_json(path):
    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def sha256_file(path):
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def fail_result(
    failures,
):
    return {
        "schema":
            "qsp.stage390.assessment-intake-result.v1",
        "stage":
            390,
        "source_stage":
            389,
        "decision":
            "fail_closed",
        "verification_status":
            "failed",
        "critical_failure_count":
            len(
                failures
            ),
        "failures":
            failures,
        "submission_present":
            True,
        "independent_reproduction_completed":
            False,
        "assessment_outcome":
            None,
        "external_assessment_completed":
            False,
        "formal_certification":
            False,
        "system_wide_formal_acceptance":
            False,
        "entire_system_quantum_safe":
            False,
        "stage389_dual_timestamp_verified":
            False,
    }


def validate_required_fields(
    data,
    required_fields,
    prefix,
):
    failures = []

    for field in required_fields:
        if field not in data:
            failures.append(
                f"{prefix}.{field}: missing"
            )

    return failures


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Verify Stage390 independent "
            "third-party assessment intake."
        )
    )

    parser.add_argument(
        "--submission",
        help=(
            "Path to third-party assessment "
            "submission JSON."
        ),
    )

    args = parser.parse_args()

    required_files = [
        STAGE389_RESULT,
        UPSTREAM_STATE,
        ASSESSMENT_CONTRACT,
        SUBMISSION_SCHEMA,
        ENVIRONMENT_SCHEMA,
        REPRODUCTION_SCHEMA,
        INTAKE_POLICY,
    ]

    missing = [
        str(
            path.relative_to(
                ROOT
            )
        )
        for path in required_files
        if not path.is_file()
    ]

    if missing:
        result = {
            "schema":
                "qsp.stage390.assessment-intake-result.v1",
            "stage":
                390,
            "decision":
                "fail_closed",
            "verification_status":
                "failed",
            "critical_failure_count":
                len(
                    missing
                ),
            "failures": [
                "required file missing: "
                + item
                for item in missing
            ],
            "submission_present":
                bool(
                    args.submission
                ),
            "external_assessment_completed":
                False,
            "formal_certification":
                False,
            "system_wide_formal_acceptance":
                False,
            "entire_system_quantum_safe":
                False,
            "stage389_dual_timestamp_verified":
                False,
        }

        print(
            json.dumps(
                result,
                indent=2,
                sort_keys=True,
            )
        )

        return 1

    upstream = read_json(
        UPSTREAM_STATE
    )

    contract = read_json(
        ASSESSMENT_CONTRACT
    )

    submission_schema = read_json(
        SUBMISSION_SCHEMA
    )

    environment_schema = read_json(
        ENVIRONMENT_SCHEMA
    )

    reproduction_schema = read_json(
        REPRODUCTION_SCHEMA
    )

    policy = read_json(
        INTAKE_POLICY
    )

    stage389 = read_json(
        STAGE389_RESULT
    )

    failures = []

    expected_stage389_sha = (
        upstream[
            "source_result"
        ][
            "sha256"
        ]
    )

    actual_stage389_sha = (
        sha256_file(
            STAGE389_RESULT
        )
    )

    if (
        actual_stage389_sha
        != expected_stage389_sha
    ):
        failures.append(
            "stage389_result_sha256_mismatch"
        )

    if (
        stage389.get(
            "decision"
        )
        != "dual_timestamp_pending"
    ):
        failures.append(
            "stage389_decision_changed"
        )

    if (
        stage389.get(
            "dual_timestamp_verified"
        )
        is not False
    ):
        failures.append(
            "stage389_dual_timestamp_state_changed"
        )

    if failures:
        result = fail_result(
            failures
        )

        print(
            json.dumps(
                result,
                indent=2,
                sort_keys=True,
            )
        )

        return 1

    if not args.submission:
        result = {
            "schema":
                "qsp.stage390.assessment-intake-result.v1",
            "stage":
                390,
            "source_stage":
                389,
            "decision":
                policy[
                    "decision_policy"
                ][
                    "no_submission"
                ],
            "verification_status":
                "ready",
            "critical_failure_count":
                0,
            "failures":
                [],
            "submission_present":
                False,
            "independent_reproduction_completed":
                False,
            "assessment_outcome":
                None,
            "upstream_binding_verified":
                True,
            "external_assessment_completed":
                False,
            "formal_certification":
                False,
            "system_wide_formal_acceptance":
                False,
            "entire_system_quantum_safe":
                False,
            "stage389_dual_timestamp_verified":
                False,
        }

        print(
            json.dumps(
                result,
                indent=2,
                sort_keys=True,
            )
        )

        return 0

    submission_path = Path(
        args.submission
    )

    if not submission_path.is_file():
        result = fail_result(
            [
                "submission file missing"
            ]
        )

        print(
            json.dumps(
                result,
                indent=2,
                sort_keys=True,
            )
        )

        return 1

    try:
        submission = read_json(
            submission_path
        )
    except Exception as exc:
        result = fail_result(
            [
                "submission JSON invalid: "
                + type(
                    exc
                ).__name__
            ]
        )

        print(
            json.dumps(
                result,
                indent=2,
                sort_keys=True,
            )
        )

        return 1

    failures.extend(
        validate_required_fields(
            submission,
            submission_schema[
                "required_fields"
            ],
            "submission",
        )
    )

    forbidden = (
        submission_schema[
            "forbidden_self_assertions"
        ]
    )

    for field in forbidden:
        if field in submission:
            failures.append(
                "forbidden_self_assertion:"
                + field
            )

    if failures:
        result = fail_result(
            failures
        )

        print(
            json.dumps(
                result,
                indent=2,
                sort_keys=True,
            )
        )

        return 1

    if (
        submission.get(
            "schema"
        )
        != "qsp.stage390.assessment-submission.v1"
    ):
        failures.append(
            "submission_schema_invalid"
        )

    if (
        submission.get(
            "stage"
        )
        != 390
    ):
        failures.append(
            "submission_stage_invalid"
        )

    assessor = submission[
        "assessor"
    ]

    failures.extend(
        validate_required_fields(
            assessor,
            submission_schema[
                "assessor"
            ][
                "required_fields"
            ],
            "assessor",
        )
    )

    if (
        assessor.get(
            "independence_declared"
        )
        is not True
    ):
        failures.append(
            "assessor_independence_not_declared"
        )

    environment = submission[
        "environment"
    ]

    failures.extend(
        validate_required_fields(
            environment,
            environment_schema[
                "required_fields"
            ],
            "environment",
        )
    )

    execution_mode = (
        environment.get(
            "execution_mode"
        )
    )

    if (
        execution_mode
        not in environment_schema[
            "allowed_execution_modes"
        ]
    ):
        failures.append(
            "environment.execution_mode_invalid"
        )

    binding = submission[
        "upstream_binding"
    ]

    failures.extend(
        validate_required_fields(
            binding,
            submission_schema[
                "upstream_binding"
            ][
                "required_fields"
            ],
            "upstream_binding",
        )
    )

    expected_commit = (
        upstream[
            "source_commit"
        ]
    )

    binding_verified = all(
        [
            binding.get(
                "stage389_result_sha256"
            )
            == expected_stage389_sha,
            binding.get(
                "stage389_commit"
            )
            == expected_commit,
            actual_stage389_sha
            == expected_stage389_sha,
        ]
    )

    if not binding_verified:
        failures.append(
            "upstream_binding_mismatch"
        )

    reproduction = submission[
        "reproduction"
    ]

    failures.extend(
        validate_required_fields(
            reproduction,
            reproduction_schema[
                "required_fields"
            ],
            "reproduction",
        )
    )

    assessment = submission[
        "assessment"
    ]

    failures.extend(
        validate_required_fields(
            assessment,
            submission_schema[
                "assessment"
            ][
                "required_fields"
            ],
            "assessment",
        )
    )

    outcome = assessment.get(
        "outcome"
    )

    if (
        outcome
        not in submission_schema[
            "assessment"
        ][
            "allowed_outcomes"
        ]
    ):
        failures.append(
            "assessment_outcome_invalid"
        )

    critical_mismatch_count = (
        reproduction.get(
            "critical_mismatch_count"
        )
    )

    if (
        not isinstance(
            critical_mismatch_count,
            int,
        )
        or isinstance(
            critical_mismatch_count,
            bool,
        )
        or critical_mismatch_count < 0
    ):
        failures.append(
            "critical_mismatch_count_invalid"
        )

    reproduction_completed = (
        reproduction.get(
            "reproduction_completed"
        )
        is True
    )

    if failures:
        result = fail_result(
            failures
        )

        print(
            json.dumps(
                result,
                indent=2,
                sort_keys=True,
            )
        )

        return 1

    derived_outcome = None

    if not reproduction_completed:
        derived_outcome = "incomplete"

    elif (
        critical_mismatch_count
        > 0
    ):
        derived_outcome = "disagreement"

    else:
        required_success = (
            reproduction_schema[
                "success_definition"
            ]
        )

        success_fields = [
            field
            for field, value
            in required_success.items()
            if value is True
        ]

        success_ok = all(
            reproduction.get(
                field
            )
            is True
            for field in success_fields
        )

        success_ok = (
            success_ok
            and critical_mismatch_count
            == 0
            and binding_verified
        )

        if success_ok:
            derived_outcome = "agreement"
        else:
            derived_outcome = "incomplete"

    if outcome != derived_outcome:
        result = fail_result(
            [
                "declared_assessment_outcome_"
                "does_not_match_derived_outcome"
            ]
        )

        print(
            json.dumps(
                result,
                indent=2,
                sort_keys=True,
            )
        )

        return 1

    if derived_outcome == "agreement":
        decision = (
            policy[
                "decision_policy"
            ][
                "valid_agreement_submission"
            ]
        )

        verification_status = (
            "agreement_received"
        )

    elif derived_outcome == "disagreement":
        decision = (
            policy[
                "decision_policy"
            ][
                "valid_disagreement_submission"
            ]
        )

        verification_status = (
            "disagreement_received"
        )

    else:
        decision = (
            policy[
                "decision_policy"
            ][
                "valid_incomplete_submission"
            ]
        )

        verification_status = (
            "incomplete"
        )

    result = {
        "schema":
            "qsp.stage390.assessment-intake-result.v1",
        "stage":
            390,
        "source_stage":
            389,
        "decision":
            decision,
        "verification_status":
            verification_status,
        "critical_failure_count":
            0,
        "failures":
            [],
        "submission_present":
            True,
        "assessor_id":
            assessor.get(
                "assessor_id"
            ),
        "assessor_independence_declared":
            True,
        "upstream_binding_verified":
            binding_verified,
        "independent_reproduction_completed":
            reproduction_completed,
        "critical_mismatch_count":
            critical_mismatch_count,
        "assessment_outcome":
            derived_outcome,
        "external_assessment_completed":
            False,
        "formal_certification":
            False,
        "system_wide_formal_acceptance":
            False,
        "entire_system_quantum_safe":
            False,
        "stage389_dual_timestamp_verified":
            False,
    }

    print(
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
        )
    )

    return 0


if __name__ == "__main__":
    sys.exit(
        main()
    )
