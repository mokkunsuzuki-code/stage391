#!/usr/bin/env python3

import argparse
import hashlib
import json
import sys
from pathlib import Path


BASE = Path("development")

STAGE390_RESULT = (
    BASE
    / "stage390"
    / "stage390_assessment_intake_result.json"
)

STAGE389_RESULT = (
    BASE
    / "stage389"
    / "stage389_dual_timestamp_result.json"
)

STAGE390_SUBMISSION_SCHEMA = (
    BASE
    / "stage390"
    / "stage390_assessment_submission_schema.json"
)

STAGE390_ENVIRONMENT_SCHEMA = (
    BASE
    / "stage390"
    / "stage390_assessor_environment_schema.json"
)

STAGE390_REPRODUCTION_SCHEMA = (
    BASE
    / "stage390"
    / "stage390_reproduction_result_schema.json"
)

STAGE390_INTAKE_POLICY = (
    BASE
    / "stage390"
    / "stage390_assessment_intake_policy.json"
)

STAGE391_UPSTREAM_STATE = (
    BASE
    / "stage391"
    / "stage391_upstream_state.json"
)

STAGE391_CONTRACT = (
    BASE
    / "stage391"
    / "stage391_adjudication_contract.json"
)

STAGE391_BINDING_POLICY = (
    BASE
    / "stage391"
    / "stage391_submission_binding_policy.json"
)

EXPECTED_STAGE390_RESULT_SHA = (
    "90f57cfdca45fe7b6f3a150302e22060"
    "ce1e6ac46d2ff2b12889ca51e8c8dc4e"
)

EXPECTED_STAGE390_COMMIT = (
    "3d9421967c407fd965d2bdfa25b413ff1c99710a"
)

EXPECTED_STAGE389_RESULT_SHA = (
    "3a8815593fd4b570b881e39806c57e32"
    "f11d7aec7f544e30481021167b2667c4"
)


def load_json(path):
    return json.loads(
        Path(path).read_text(
            encoding="utf-8"
        )
    )


def sha256_file(path):
    h = hashlib.sha256()

    with Path(path).open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            h.update(chunk)

    return h.hexdigest()


def fail_result(*failures):
    return {
        "schema":
            "qsp.stage391.adjudication-result.v1",

        "stage":
            391,

        "source_stage":
            390,

        "decision":
            "third_party_submission_rejected",

        "verification_status":
            "fail_closed",

        "submission_present":
            True,

        "submission_origin":
            None,

        "independent_reproduction_completed":
            False,

        "assessment_outcome":
            "invalid_submission",

        "external_assessment_completed":
            False,

        "verified_third_party_agreement":
            False,

        "verified_third_party_disagreement":
            False,

        "critical_failure_count":
            len(failures),

        "failures":
            list(failures),

        "formal_certification":
            False,

        "system_wide_formal_acceptance":
            False,

        "entire_system_quantum_safe":
            False,

        "stage389_dual_timestamp_verified":
            False,

        "stage389_state":
            "dual_timestamp_pending",
    }


def pending_result():
    return {
        "schema":
            "qsp.stage391.adjudication-result.v1",

        "stage":
            391,

        "source_stage":
            390,

        "decision":
            "third_party_submission_pending",

        "verification_status":
            "waiting_for_external_submission",

        "submission_present":
            False,

        "submission_origin":
            None,

        "independent_reproduction_completed":
            False,

        "assessment_outcome":
            None,

        "external_assessment_completed":
            False,

        "verified_third_party_agreement":
            False,

        "verified_third_party_disagreement":
            False,

        "critical_failure_count":
            0,

        "failures":
            [],

        "formal_certification":
            False,

        "system_wide_formal_acceptance":
            False,

        "entire_system_quantum_safe":
            False,

        "stage389_dual_timestamp_verified":
            False,

        "stage389_state":
            "dual_timestamp_pending",
    }


def require_fields(obj, fields, prefix):
    missing = []

    for field in fields:
        if field not in obj:
            missing.append(
                f"{prefix}.{field}"
            )

    return missing


def validate_submission(data):
    failures = []

    submission_schema = load_json(
        STAGE390_SUBMISSION_SCHEMA
    )

    environment_schema = load_json(
        STAGE390_ENVIRONMENT_SCHEMA
    )

    reproduction_schema = load_json(
        STAGE390_REPRODUCTION_SCHEMA
    )

    intake_policy = load_json(
        STAGE390_INTAKE_POLICY
    )

    upstream = load_json(
        STAGE391_UPSTREAM_STATE
    )

    contract = load_json(
        STAGE391_CONTRACT
    )

    binding_policy = load_json(
        STAGE391_BINDING_POLICY
    )

    stage390_result = load_json(
        STAGE390_RESULT
    )

    stage389_result = load_json(
        STAGE389_RESULT
    )

    actual_stage390_sha = sha256_file(
        STAGE390_RESULT
    )

    actual_stage389_sha = sha256_file(
        STAGE389_RESULT
    )

    if (
        actual_stage390_sha
        != EXPECTED_STAGE390_RESULT_SHA
    ):
        failures.append(
            "actual_stage390_result_sha_mismatch"
        )

    if (
        actual_stage389_sha
        != EXPECTED_STAGE389_RESULT_SHA
    ):
        failures.append(
            "actual_stage389_result_sha_mismatch"
        )

    if (
        stage389_result.get("decision")
        != "dual_timestamp_pending"
    ):
        failures.append(
            "actual_stage389_decision_changed"
        )

    if (
        stage389_result.get(
            "dual_timestamp_verified"
        )
        is not False
    ):
        failures.append(
            "actual_stage389_timestamp_state_promoted"
        )

    # Stage391 own upstream invariants.
    if (
        upstream.get(
            "expected_stage390_result_sha256"
        )
        != EXPECTED_STAGE390_RESULT_SHA
    ):
        failures.append(
            "stage391_upstream_stage390_result_sha_mismatch"
        )

    if (
        upstream.get(
            "expected_stage390_commit"
        )
        != EXPECTED_STAGE390_COMMIT
    ):
        failures.append(
            "stage391_upstream_stage390_commit_mismatch"
        )

    if (
        stage390_result.get("decision")
        != "third_party_assessment_ready"
    ):
        failures.append(
            "stage390_not_assessment_ready"
        )

    if (
        stage390_result.get(
            "external_assessment_completed"
        )
        is not False
    ):
        failures.append(
            "stage390_external_assessment_state_invalid"
        )

    # Top-level Stage390 submission contract.
    failures.extend(
        require_fields(
            data,
            submission_schema["required_fields"],
            "submission",
        )
    )

    if failures:
        return fail_result(*failures)

    if (
        data.get("schema")
        != submission_schema.get("schema")
    ):
        failures.append(
            "submission_schema_mismatch"
        )

    if data.get("stage") != 390:
        failures.append(
            "submission_stage_mismatch"
        )

    assessor = data.get("assessor")

    environment = data.get("environment")

    upstream_binding = data.get(
        "upstream_binding"
    )

    reproduction = data.get(
        "reproduction"
    )

    assessment = data.get(
        "assessment"
    )

    if not isinstance(assessor, dict):
        failures.append(
            "assessor_not_object"
        )

    if not isinstance(environment, dict):
        failures.append(
            "environment_not_object"
        )

    if not isinstance(upstream_binding, dict):
        failures.append(
            "upstream_binding_not_object"
        )

    if not isinstance(reproduction, dict):
        failures.append(
            "reproduction_not_object"
        )

    if not isinstance(assessment, dict):
        failures.append(
            "assessment_not_object"
        )

    if failures:
        return fail_result(*failures)

    # Assessor.
    failures.extend(
        require_fields(
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
            "independence_declaration_missing_or_false"
        )

    assessor_id = assessor.get(
        "assessor_id"
    )

    if (
        not isinstance(assessor_id, str)
        or not assessor_id.strip()
    ):
        failures.append(
            "assessor_id_invalid"
        )

    # Environment.
    failures.extend(
        require_fields(
            environment,
            environment_schema[
                "required_fields"
            ],
            "environment",
        )
    )

    execution_mode = environment.get(
        "execution_mode"
    )

    if (
        execution_mode
        not in environment_schema[
            "allowed_execution_modes"
        ]
    ):
        failures.append(
            "execution_mode_invalid"
        )

    # Upstream binding defined by Stage390.
    failures.extend(
        require_fields(
            upstream_binding,
            submission_schema[
                "upstream_binding"
            ][
                "required_fields"
            ],
            "upstream_binding",
        )
    )

    expected_stage389_sha = (
        submission_schema[
            "upstream_binding"
        ][
            "expected_stage389_result_sha256"
        ]
    )

    expected_stage389_commit = (
        submission_schema[
            "upstream_binding"
        ][
            "expected_stage389_commit"
        ]
    )

    if (
        upstream_binding.get(
            "stage389_result_sha256"
        )
        != expected_stage389_sha
    ):
        failures.append(
            "stage389_result_sha_binding_mismatch"
        )

    if (
        upstream_binding.get(
            "stage389_commit"
        )
        != expected_stage389_commit
    ):
        failures.append(
            "stage389_commit_binding_mismatch"
        )

    # Reproduction summary contract.
    failures.extend(
        require_fields(
            reproduction,
            submission_schema[
                "reproduction"
            ][
                "required_fields"
            ],
            "reproduction",
        )
    )

    mismatch_count = reproduction.get(
        "critical_mismatch_count"
    )

    if (
        isinstance(mismatch_count, bool)
        or not isinstance(
            mismatch_count,
            int,
        )
        or mismatch_count < 0
    ):
        failures.append(
            "critical_mismatch_count_invalid"
        )

    reproduction_completed = (
        reproduction.get(
            "reproduction_completed"
        )
    )

    if not isinstance(
        reproduction_completed,
        bool,
    ):
        failures.append(
            "reproduction_completed_not_boolean"
        )

    # Optional detailed reproduction_result may be
    # supplied by third parties. If present, validate
    # it against the Stage390 reproduction schema.
    reproduction_result = data.get(
        "reproduction_result"
    )

    if reproduction_result is not None:

        if not isinstance(
            reproduction_result,
            dict,
        ):
            failures.append(
                "reproduction_result_not_object"
            )

        else:
            failures.extend(
                require_fields(
                    reproduction_result,
                    reproduction_schema[
                        "required_fields"
                    ],
                    "reproduction_result",
                )
            )

            detail_mismatch = (
                reproduction_result.get(
                    "critical_mismatch_count"
                )
            )

            if (
                isinstance(
                    detail_mismatch,
                    bool,
                )
                or not isinstance(
                    detail_mismatch,
                    int,
                )
                or detail_mismatch < 0
            ):
                failures.append(
                    "reproduction_result_mismatch_count_invalid"
                )

            if (
                isinstance(
                    mismatch_count,
                    int,
                )
                and not isinstance(
                    mismatch_count,
                    bool,
                )
                and isinstance(
                    detail_mismatch,
                    int,
                )
                and not isinstance(
                    detail_mismatch,
                    bool,
                )
                and mismatch_count
                != detail_mismatch
            ):
                failures.append(
                    "reproduction_mismatch_count_inconsistent"
                )

    # Assessment.
    failures.extend(
        require_fields(
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

    allowed_outcomes = (
        submission_schema[
            "assessment"
        ][
            "allowed_outcomes"
        ]
    )

    if outcome not in allowed_outcomes:
        failures.append(
            "assessment_outcome_invalid"
        )

    # Forbidden self assertions anywhere at top level.
    for forbidden in submission_schema[
        "forbidden_self_assertions"
    ]:
        if forbidden in data:
            failures.append(
                "forbidden_self_assertion:"
                + forbidden
            )

    # Stage391 origin rule:
    # Stage390 did not define submission_origin,
    # so Stage391 treats absence as unqualified.
    submission_origin = data.get(
        "submission_origin"
    )

    if submission_origin is None:
        failures.append(
            "stage391_submission_origin_missing"
        )

    elif (
        submission_origin
        not in contract[
            "accepted_submission_origins"
        ]
    ):
        failures.append(
            "submission_origin_not_independent_third_party"
        )

    if failures:
        result = fail_result(*failures)
        result["submission_origin"] = (
            submission_origin
        )
        return result

    # Classification logic follows Stage390 policy.
    classification = intake_policy[
        "classification"
    ]

    # Agreement.
    if outcome == "agreement":

        if reproduction_completed is not True:
            return fail_result(
                "agreement_requires_reproduction_completed"
            )

        if mismatch_count != 0:
            return fail_result(
                "agreement_requires_zero_mismatch"
            )

        if (
            reproduction.get(
                "deterministic_result_obtained"
            )
            is not True
        ):
            return fail_result(
                "agreement_requires_deterministic_result"
            )

        if (
            reproduction.get(
                "reference_result_compared"
            )
            is not True
        ):
            return fail_result(
                "agreement_requires_reference_comparison"
            )

        return {
            "schema":
                "qsp.stage391.adjudication-result.v1",

            "stage":
                391,

            "source_stage":
                390,

            "decision":
                "third_party_reproduction_agreement_verified",

            "verification_status":
                "verified",

            "submission_present":
                True,

            "submission_origin":
                submission_origin,

            "independent_reproduction_completed":
                True,

            "assessment_outcome":
                "agreement",

            "external_assessment_completed":
                True,

            "verified_third_party_agreement":
                True,

            "verified_third_party_disagreement":
                False,

            "critical_failure_count":
                0,

            "failures":
                [],

            "formal_certification":
                False,

            "system_wide_formal_acceptance":
                False,

            "entire_system_quantum_safe":
                False,

            "stage389_dual_timestamp_verified":
                False,

            "stage389_state":
                "dual_timestamp_pending",
        }

    # Disagreement.
    if outcome == "disagreement":

        if reproduction_completed is not True:
            return fail_result(
                "disagreement_requires_reproduction_completed"
            )

        if mismatch_count <= 0:
            return fail_result(
                "disagreement_requires_positive_mismatch"
            )

        return {
            "schema":
                "qsp.stage391.adjudication-result.v1",

            "stage":
                391,

            "source_stage":
                390,

            "decision":
                "third_party_reproduction_disagreement_verified",

            "verification_status":
                "verified_disagreement",

            "submission_present":
                True,

            "submission_origin":
                submission_origin,

            "independent_reproduction_completed":
                True,

            "assessment_outcome":
                "disagreement",

            "external_assessment_completed":
                True,

            "verified_third_party_agreement":
                False,

            "verified_third_party_disagreement":
                True,

            "critical_failure_count":
                0,

            "failures":
                [],

            "formal_certification":
                False,

            "system_wide_formal_acceptance":
                False,

            "entire_system_quantum_safe":
                False,

            "stage389_dual_timestamp_verified":
                False,

            "stage389_state":
                "dual_timestamp_pending",
        }

    # Incomplete.
    if outcome == "incomplete":

        if reproduction_completed is not False:
            return fail_result(
                "incomplete_requires_reproduction_completed_false"
            )

        return {
            "schema":
                "qsp.stage391.adjudication-result.v1",

            "stage":
                391,

            "source_stage":
                390,

            "decision":
                "third_party_reproduction_incomplete",

            "verification_status":
                "incomplete",

            "submission_present":
                True,

            "submission_origin":
                submission_origin,

            "independent_reproduction_completed":
                False,

            "assessment_outcome":
                "incomplete",

            "external_assessment_completed":
                False,

            "verified_third_party_agreement":
                False,

            "verified_third_party_disagreement":
                False,

            "critical_failure_count":
                0,

            "failures":
                [],

            "formal_certification":
                False,

            "system_wide_formal_acceptance":
                False,

            "entire_system_quantum_safe":
                False,

            "stage389_dual_timestamp_verified":
                False,

            "stage389_state":
                "dual_timestamp_pending",
        }

    return fail_result(
        "unreachable_classification_state"
    )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Stage391 independent third-party "
            "reproduction adjudication verifier"
        )
    )

    parser.add_argument(
        "--submission",
        default=None,
        help=(
            "Path to independent third-party "
            "submission JSON. Omit for pending state."
        ),
    )

    args = parser.parse_args()

    if args.submission is None:

        result = pending_result()

    else:

        try:
            data = load_json(
                args.submission
            )

        except (
            OSError,
            json.JSONDecodeError,
        ) as exc:

            result = fail_result(
                "submission_load_failed:"
                + type(exc).__name__
            )

        else:

            if not isinstance(
                data,
                dict,
            ):
                result = fail_result(
                    "submission_root_not_object"
                )
            else:
                result = validate_submission(
                    data
                )

    json.dump(
        result,
        sys.stdout,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )

    sys.stdout.write("\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
