# Findings: Indiana hospital readmissions

Independent portfolio analysis created September 2026. CMS FY 2026 release;
measurement period July 1, 2021 through June 30, 2024. Results describe this
historical reporting period, not present-day hospital performance.

## Decision question

Which condition-specific patterns should an Indiana quality team investigate,
and how does missing published information affect that shortlist?

## Findings and next steps

1. **COPD is a starting point for review.** 34 of 68 Indiana hospitals
   with published COPD ratios (50.0%) have a ratio above 1,
   compared with 47.2% in the national source population.
   This 2.8 percentage-point descriptive difference is
   not a significance test, payment penalty or estimate of avoidable readmissions.
   Next: review measure volumes and facility context before choosing hospitals
   for a care-transition review. No intervention or savings is claimed here.
2. **Coverage varies by condition.** Heart failure has 72 published ratios among
   82 Indiana source hospitals; coronary bypass has 24. Missing ratios are
   excluded from that measure's denominator, not treated as good performance.
   Next: examine source footnotes and whether the service is offered before
   comparing programs with different reporting coverage.
3. **A volume filter changes the cohort.** Nationally, 3,683 rows have
   a published ratio but unavailable discharge counts. Default results retain
   them. Any positive volume filter excludes them visibly and applies the same
   rule to Indiana and national benchmarks. These are analyst-selected
   sensitivity settings, not CMS reporting eligibility cutoffs.

## Baseline condition comparisons (no volume filter)

| Condition | Indiana published / source | Indiana above 1 | National above 1 |
|---|---:|---:|---:|
| Heart failure | 72 / 82 | 48.6% | 48.9% |
| COPD | 68 / 82 | 50.0% | 47.2% |
| Pneumonia | 71 / 82 | 42.3% | 46.8% |
| Heart attack | 44 / 82 | 43.2% | 49.7% |
| Coronary bypass | 24 / 82 | 45.8% | 49.9% |
| Hip / knee replacement | 42 / 82 | 38.1% | 47.9% |

## Interpretation

- Grain: one hospital × condition/procedure × common measurement period.
- Excess readmission ratio = CMS-published predicted / expected readmission rate.
  The project uses the published ratio; it does not estimate a new risk model.
- Above-one share = hospital-condition rows with ERR > 1 / rows eligible for
  the selected condition and volume filter. Every eligible hospital gets equal
  weight. This is a share of hospitals, not a patient readmission rate.
- National means all hospitals in this source file, including Indiana. It is
  descriptive context, not CMS's dual-eligibility peer-group payment benchmark.
- The median summarizes hospital ratios. No pooled patient rate, inferred
  suppressed count, financial penalty or all-condition composite is calculated.
- This snapshot cannot establish a time trend, causes, avoidability, or the
  effect of a quality intervention. No confidence intervals are provided by
  this extract, and no significance claim is made.

## Verification

48 independently reconciled region × condition × volume summaries; source
checksum and totals; unique keys; six source measure rows per facility;
foreign keys; published-ratio rounding check. Raw missing/suppression tokens
and source footnotes remain visible in the Indiana export.
