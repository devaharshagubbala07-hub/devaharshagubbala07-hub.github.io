# Data quality before the denominator

All figures below come from intentionally flawed synthetic demo records. They are
not measurements of the academic team's original system or a production feed.

- **33 input entries = 23 loaded + 10 quarantined.**
- **1 loaded record(s) have a warning.** Missing birth dates
  stay null; the pipeline does not fabricate a demographic value to pass a check.
- **6 of 8 loaded patients** have at least
  one accepted observation with status exactly `final`. There are
  10 final observation rows: counting rows instead of
  distinct patients would overstate coverage.
- **2 loaded patients have no accepted final observation.**
  A left join keeps them in the reporting denominator. Absence from this fixture
  is not evidence that someone missed care.
- All 5 reconciliation checks pass.

## Decision

Resolve duplicate identities and patient references before reporting. Review
quarantined resources with the source owner; do not guess which duplicate is
authoritative or replace clinical codes with more specific concepts.

## Scope

The pipeline implements a small local reporting profile for Patient, scalar
heart-rate Observation and single-coding Condition resources. A valid FHIR
resource can fall outside this profile. Passing these checks is not full FHIR
conformance, clinical validation, or evidence of privacy compliance.
