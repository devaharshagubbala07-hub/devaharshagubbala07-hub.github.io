# Hospital Readmissions & Quality Benchmarking

**An independent Python and SQL analysis of Indiana hospitals, with national context.**

[Open the interactive case study](https://devaharshagubbala07-hub.github.io/projects/readmissions/) · [Read the findings](outputs/findings.md) · [Inspect the source](source.json)

## The question

Where should an Indiana hospital quality team investigate first, and how does missing published information affect the comparison?

The project uses real, public CMS Hospital Readmissions Reduction Program data. It combines a reproducible analysis, a normalized SQLite model, explicit cohort rules, an interactive hospital explorer and a written decision brief.

## Findings

- **34 of 68 Indiana hospitals with published COPD ratios (50.0%) are above 1**, compared with **47.2% nationally**. This is a descriptive hospital-share comparison, not a significance result, patient readmission rate or payment-penalty calculation.
- **Reporting coverage differs:** 72 of 82 Indiana source hospitals have a published heart failure ratio; only 24 have a published coronary bypass ratio. Comparisons need condition-specific denominators.
- **3,683 national rows have a published ratio but unavailable discharge counts.** They remain in the default analysis. Optional volume filters show exactly how many rows are excluded and why.

A practical next step is a condition-specific review of hospital volumes, service availability, source footnotes and care-transition processes. The project does not claim that an intervention occurred or that savings were achieved.

## Run it

Python **3.11 or later**; standard library only. No paid services or API keys.

From this folder:

```bash
python download_source.py
python analysis.py
python -m unittest discover -p "test_*.py" -v
python build_page.py
```

The download script retrieves the pinned 2.1 MB CMS CSV and checks its SHA-256 hash. It reuses an already verified local copy. If CMS removes the URL, obtain the exact release separately, place it at `data/hrrp.csv`, and verify the hash in `source.json`; do not silently substitute a newer release.

From the repository root, start `python -m http.server 8000`, then open `http://localhost:8000/projects/readmissions/`. HTTP is required for the browser to load the results JSON. The page includes complete static baseline findings and charts without JavaScript.

## Data and time

| Item | Value |
|---|---|
| Publisher | Centers for Medicare & Medicaid Services |
| Dataset | HRRP, `9n3s-kdb3` |
| Program year | FY 2026 |
| Observation period | July 1, 2021–June 30, 2024 |
| Catalog modified / released | January 26, 2026 / August 13, 2026 |
| Retrieved / project created | September 26, 2026 |
| Source grain | Hospital × condition/procedure × common observation period |
| Source size | 18,330 rows, 3,055 hospitals, 6 measures |
| Indiana subset | 492 rows, 82 hospitals |

Source dates describe the data, not when this project was completed. The original CSV is retrieved from CMS; derived Indiana rows and benchmark summaries are included here. No patient-level or employer data is used.

## Model and measures

`Facility → Result ← Measure`

- `facility` holds one row per six-character CMS facility ID, with name and state.
- `measure` holds the six condition/procedure identifiers and display labels.
- `result` has a `(facility_id, measure_id)` primary key and foreign keys to both dimensions.
- IDs retain leading zeros. Duplicate keys, inconsistent facility identities, unfamiliar numeric tokens and mixed measurement periods stop processing.
- Source footnotes and original missing/suppression tokens are preserved. Suppressed counts are never estimated.

**Published excess readmission ratio (ERR):** CMS-published predicted / expected readmission rate for a hospital and condition. The pipeline checks the component ratio within 0.0001, allowing for published rounding; the analysis uses the published ERR.

**Share above 1:** eligible hospital-condition rows with ERR > 1 divided by eligible rows for the selected condition. A ratio exactly 1 belongs to a separate neutral count. Each eligible hospital has equal weight.

**Median ERR:** the middle eligible hospital ratio, or average of the two middle ratios, calculated with SQL window functions. This is not a pooled patient readmission rate.

**National context:** all hospitals in the source file, including Indiana. It is not a matched comparator or the official dual-eligibility peer-group payment benchmark.

## Cohort decisions

Default: retain every numeric published ratio even if discharge volume is unavailable.

Optional minimum published discharge settings of 25, 100 and 250 are **analyst-selected sensitivity settings**, not CMS reporting eligibility rules. The same setting applies to both regions. Exclusions are assigned in this order:

1. Missing published ratio.
2. Positive minimum selected, but discharge count unavailable.
3. Discharge count below the selected minimum.
4. Eligible.

The four groups are mutually exclusive and reconcile to all source hospitals for that condition. Empty denominators return null, not zero. The dashboard reports the denominator and exclusions beside the headline measures. Table search and status filters do not change cohort KPIs.

## Files worth reading

| File | Purpose |
|---|---|
| [analysis.py](analysis.py) | Source validation, model loading, independent reconciliations and exports |
| [sql/schema.sql](sql/schema.sql) | Keys, relationships and constraints |
| [sql/cohort_summary.sql](sql/cohort_summary.sql) | Cohort definitions, ratios and window-based median |
| [outputs/findings.md](outputs/findings.md) | Finding, implication, next step and limitations |
| [outputs/condition_benchmarks.csv](outputs/condition_benchmarks.csv) | All 48 region-condition-volume comparisons |
| [outputs/indiana_hospital_measures.csv](outputs/indiana_hospital_measures.csv) | All 492 Indiana rows with original tokens and footnotes |
| [test_analysis.py](test_analysis.py) | Nine edge-case tests |
| [INTERVIEW_GUIDE.md](INTERVIEW_GUIDE.md) | Questions to understand before presenting the work |

## Verification and limits

The pipeline independently reconciles all **48** SQL summaries against Python counts, shares and medians. It also checks source totals, one row per key, six source measures per facility, foreign keys and published-ratio rounding. Nine automated tests cover missing volume versus missing ratios, exact threshold boundaries, zero values, odd/even/empty medians, geographic denominators, leading-zero IDs, duplicate keys, nonfinite numbers and source tampering.

This is a historical aggregate-data study. It cannot show a current hospital trend, predict an individual patient's readmission, establish causation, prove avoidability, or estimate intervention savings. The extract provides no confidence intervals, so differences are not labeled statistically significant. An ERR above 1 alone does not establish an HRRP payment penalty.

## Project origin

Developed with AI assistance in **September 2026** as an independent portfolio project for Devaharsha Gubbala. It is separate from graduate coursework and Merative work. [Provenance](provenance.json).

## Primary references

- [CMS dataset](https://data.cms.gov/provider-data/dataset/9n3s-kdb3)
- [CMS hospital data dictionary](https://data.cms.gov/provider-data/sites/default/files/data_dictionaries/hospital/HOSPITAL_Data_Dictionary.pdf)
- [CMS HRRP program and payment context](https://www.cms.gov/medicare/payment/prospective-payment-systems/acute-inpatient-pps/hospital-readmissions-reduction-program-hrrp)
- [Pinned release, dates and checksum](source.json)
