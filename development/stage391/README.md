# Stage391 — Independent Third-Party Reproduction Verification & Assessment Adjudication Gate

**第三者独立再現検証・外部評価判定ゲート**

Stage391 extends Stage390 without modifying the canonical Stage390 result or the preserved Stage389 timestamp state.

Stage390 established the public intake interface for independent third-party reproduction and assessment submissions.

Stage391 adds the executable verification and adjudication layer that can validate a submitted third-party assessment, verify its upstream bindings and independence requirements, and classify the result as:

- agreement
- disagreement
- incomplete
- invalid submission

Stage391 does not treat a self-test, smoke-test, developer fixture, or internal CI result as an independent third-party assessment.

## Current Stage391 State

Current decision:

`third_party_submission_pending`

Verification status:

`waiting_for_external_submission`

Current authoritative state:

- `submission_present = false`
- `submission_origin = null`
- `independent_reproduction_completed = false`
- `assessment_outcome = null`
- `external_assessment_completed = false`
- `verified_third_party_agreement = false`
- `verified_third_party_disagreement = false`
- `critical_failure_count = 0`

No actual independent third-party submission has been received or accepted yet.

Stage391 therefore remains in a pending intake state.

## Stage390 Upstream State

Stage391 is bound to the preserved Stage390 canonical result.

- Stage390 decision: `third_party_assessment_ready`
- Stage390 canonical result SHA-256: `90f57cfdca45fe7b6f3a150302e22060ce1e6ac46d2ff2b12889ca51e8c8dc4e`
- Expected Stage390 commit: `3d9421967c407fd965d2bdfa25b413ff1c99710a`

Stage391 does not modify or replace Stage390 evidence.

## Stage389 Preservation State

Stage391 also preserves the Stage389 timestamp result.

- Stage389 state: `dual_timestamp_pending`
- Stage389 canonical result SHA-256: `3a8815593fd4b570b881e39806c57e32f11d7aec7f544e30481021167b2667c4`
- Stage389 dual timestamp verified: `false`

Stage391 cannot promote the Stage389 OpenTimestamps state.

OpenTimestamps final verification remains the responsibility of Stage389 after the required Bitcoin chain data becomes available.

## Independent Submission Requirement

Only an actual submission with:

`submission_origin = independent_third_party`

may qualify for independent third-party assessment adjudication.

The following origins cannot qualify as external assessment:

- `self_test`
- `smoke_test`
- `developer_fixture`
- `internal_ci`

These may be used only for implementation and regression testing.

They must not set:

`external_assessment_completed = true`

## Agreement

A submission may be classified as verified agreement only when the Stage391 verifier confirms all required conditions.

At minimum:

- independent third-party origin
- valid independence declaration
- valid Stage389 result SHA-256 binding
- valid Stage389 commit binding
- reproduction completed
- deterministic result obtained
- reference result compared
- critical mismatch count equals zero
- no forbidden self-assertion
- no fail-closed violation

Successful verified classification:

`third_party_reproduction_agreement_verified`

This state is not currently active.

## Disagreement

A valid independent reproduction may produce a result different from the QSP reference result.

Stage391 preserves that disagreement rather than silently converting it into failure or success.

Verified disagreement requires:

- valid independent submission
- reproduction completed
- positive critical mismatch count

Verified classification:

`third_party_reproduction_disagreement_verified`

A disagreement is a valid assessment result and may identify environment differences, hidden assumptions, implementation differences, or reproducibility defects.

This state is not currently active.

## Incomplete

A valid submission may be incomplete when independent reproduction could not be completed.

Examples may include:

- environment incompatibility
- unavailable dependency
- execution interruption
- incomplete evidence

Classification:

`third_party_reproduction_incomplete`

An incomplete result cannot be promoted to agreement.

## Invalid Submission

Invalid or contradictory submissions are rejected Fail-Closed.

Classification:

`third_party_submission_rejected`

Examples include:

- self-test presented as independent assessment
- smoke-test presented as independent assessment
- missing independence declaration
- Stage389 result SHA-256 mismatch
- Stage389 commit mismatch
- agreement with non-zero mismatch count
- disagreement with zero mismatch count
- incomplete outcome with reproduction completed
- negative mismatch count
- Boolean mismatch count
- forbidden external-assessment self-assertion
- forbidden formal-certification self-assertion
- Stage389 timestamp self-promotion
- missing required fields
- invalid execution mode
- malformed JSON

## Fail-Closed Regression Verification

Stage391 currently includes:

- `16 / 16 PASS` negative Fail-Closed regression tests
- `3 / 3 PASS` classification-path fixtures

The classification fixtures verify that the adjudication logic can distinguish:

- agreement
- disagreement
- incomplete

These fixtures are test data only.

They are not real external assessments.

They do not change the authoritative Stage391 state.

## Canonical Stage391 Result

Current canonical Stage391 result SHA-256:

`ed644d11bd49f67f89cfda50364d619066b4da3a36bf1fb26b38e111b6092b23`

Canonical result:

`stage391_adjudication_result.json`

SHA-256 record:

`stage391_adjudication_result.sha256`

The current canonical result remains:

`third_party_submission_pending`

## Mandatory Non-Claims

The current Stage391 state explicitly does not claim:

- `external_assessment_completed = true`
- `formal_certification = true`
- `system_wide_formal_acceptance = true`
- `entire_system_quantum_safe = true`
- `stage389_dual_timestamp_verified = true`

The authoritative values remain:

- `external_assessment_completed = false`
- `formal_certification = false`
- `system_wide_formal_acceptance = false`
- `entire_system_quantum_safe = false`
- `stage389_dual_timestamp_verified = false`

## Preservation Boundary

Stage391 does not delete, replace, or overwrite Stage390, Stage389, or earlier canonical verification evidence.

Stage391 is an additive verification and adjudication layer.

## Publication Boundary

The Stage391 public layer must not publish:

- private core
- private directories
- secret credentials
- authentication tokens
- seeds
- private keys
- raw RFC3161 responses
- raw OpenTimestamps proofs
- raw QKD secret material

Only reviewed public verification and assessment metadata may be published.

## Stage391 License

This project is licensed under the MIT License.

See the repository-level:

`LICENSE`

The MIT License applies to the published source code and documentation in this repository.

It does not override confidentiality requirements, private-material restrictions, security boundaries, or applicable third-party licenses.
