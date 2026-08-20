# Stage390 — Independent Third-Party Reproduction & Assessment Intake Gate

日本語:

**第三者独立再現・外部評価受入ゲート**

Stage390 extends Stage389 without replacing, deleting, or modifying the Stage389 verification result.

Its purpose is to provide a deterministic and Fail-Closed interface through which an independent third party can reproduce reviewed QSP evidence and submit an assessment result.

Stage390 does not claim that an external assessment has already been completed.

## Stage390 Position

The current flow is:

Stage388:

Independent Assessment Evidence Package

↓

Stage389:

Dual External Timestamp Anchoring & Verification Gate

↓

Stage390:

Independent Third-Party Reproduction & Assessment Intake Gate

↓

External Assessor

↓

Independent Reproduction Result

↓

Agreement / Disagreement / Incomplete

Stage390 converts the previous assessment-readiness evidence into an executable intake interface for independent third-party reproduction.

## Stage389 Upstream State

Stage390 preserves the Stage389 authoritative result without promoting its timestamp state.

Current inherited Stage389 state:

`decision = dual_timestamp_pending`

`rfc3161_verified = true`

`opentimestamps_proof_present = true`

`opentimestamps_verified = false`

`dual_timestamp_verified = false`

The OpenTimestamps state remains incomplete because the local Bitcoin verification environment does not yet provide the required chain data.

Stage390 does not reinterpret this condition as success.

## Current Stage390 Decision

The current Stage390 decision is:

`third_party_assessment_ready`

Current state:

`submission_present = false`

`upstream_binding_verified = true`

`independent_reproduction_completed = false`

`external_assessment_completed = false`

`formal_certification = false`

`system_wide_formal_acceptance = false`

`entire_system_quantum_safe = false`

`stage389_dual_timestamp_verified = false`

This means the independent assessment intake interface is ready, but no real independent third-party assessment has yet been received.

## Assessment Submission Model

Stage390 accepts a machine-readable independent assessment submission.

The submission must contain:

- assessor identity
- independence declaration
- execution environment
- Stage389 upstream binding
- reproduction state
- assessment outcome
- findings

The supported assessment outcomes are:

`agreement`

`disagreement`

`incomplete`

The declared outcome is not blindly trusted.

Stage390 derives the effective outcome from the submitted reproduction state and rejects inconsistent claims.

## Independent Assessor Requirement

The assessor submission must explicitly declare:

`independence_declared = true`

This declaration is structurally required.

However, Stage390 does not claim that a submitted identity has been institutionally certified as independent.

That distinction remains outside the current Stage390 guarantee.

## Upstream Binding

The Stage390 intake contract is bound to:

Stage389 result SHA-256:

`3a8815593fd4b570b881e39806c57e32f11d7aec7f544e30481021167b2667c4`

Stage389 source commit:

`65c881d6c4a27cc9d49726c998b2fc96de48b117`

A submission referring to a different Stage389 result hash or commit is rejected Fail-Closed.

## Deterministic Canonical Result

The current no-submission readiness result is deterministic.

Canonical result:

`stage390_assessment_intake_result.json`

Canonical SHA-256:

`90f57cfdca45fe7b6f3a150302e22060ce1e6ac46d2ff2b12889ca51e8c8dc4e`

Repeated independent executions of the Stage390 verifier produced byte-for-byte identical results and the same SHA-256 value.

## Decision Model

No submission:

`third_party_assessment_ready`

Valid incomplete submission:

`third_party_assessment_incomplete`

Valid disagreement submission:

`third_party_assessment_disagreement_received`

Valid agreement submission:

`third_party_reproduction_agreement_received`

Invalid, malformed, inconsistent, forged, or upstream-mismatched submission:

`fail_closed`

## Important External Assessment Distinction

A successful Stage390 reproduction agreement does not automatically mean:

`external_assessment_completed = true`

The current implementation intentionally preserves:

`external_assessment_completed = false`

because a fixture, test submission, or structurally valid submission is not by itself proof of a formally completed external assessment process.

Stage390 separates:

independent reproduction intake

from:

formal external assessment completion

and from:

formal certification.

## Fail-Closed Negative Regression Verification

Stage390 currently verifies 12 negative cases:

1. Forged external assessment completion is rejected.
2. Forged formal certification is rejected.
3. Stage389 result SHA-256 tampering is rejected.
4. Stage389 commit tampering is rejected.
5. Missing independence declaration is rejected.
6. Invalid execution mode is rejected.
7. Incomplete reproduction cannot claim agreement.
8. Zero-mismatch reproduction cannot claim disagreement.
9. Negative critical mismatch count is rejected.
10. Boolean critical mismatch count is rejected.
11. Missing required fields are rejected.
12. Malformed JSON is rejected.

Current regression result:

`12 / 12 PASS`

The negative tests run in isolated temporary directories and do not alter the canonical Stage390 readiness result.

## Mandatory Non-Claims

The following remain false:

`external_assessment_completed = false`

`formal_certification = false`

`system_wide_formal_acceptance = false`

`entire_system_quantum_safe = false`

`stage389_dual_timestamp_verified = false`

Stage390 does not claim certification, total system security, completed third-party assessment, or completed Stage389 dual timestamp verification.

## Publication Boundary

Stage390 preserves the QSP publication boundary.

The public repository must not contain:

- private core
- private directories
- secrets
- credentials
- tokens
- seeds
- private keys
- raw RFC3161 timestamp responses
- raw OpenTimestamps proofs
- raw QKD secret material

Only reviewed public contracts, schemas, verifier code, regression tests, deterministic results, hashes, and documentation may be published.

## Stage389 Preservation

Stage390 must not modify the authoritative Stage389 result.

Expected Stage389 result SHA-256:

`3a8815593fd4b570b881e39806c57e32f11d7aec7f544e30481021167b2667c4`

Stage389 remains:

`dual_timestamp_pending`

until its own OpenTimestamps verification completes successfully.

## Stage390 License

This project is licensed under the MIT License.

See the repository-level:

`LICENSE`

The MIT License applies to the published source code and documentation in this repository.

It does not override confidentiality requirements, private-material restrictions, security boundaries, or applicable third-party licenses.
