# Understand the project before presenting it

This guide is for learning and discussion. Describe this as an independent portfolio project created in September 2026 with AI assistance. Do not present it as master's coursework or a Merative client assignment.

## Questions to be ready for

1. **What decision does the analysis support?** Choosing condition-specific hospital results for further quality review. It does not prove a care problem or prescribe an intervention.
2. **What does each row represent?** One hospital and one condition/procedure over the common July 2021–June 2024 period. Six measures per hospital means the source row count is six times the hospital count.
3. **Why not count missing values as zero?** Unavailable information is not evidence of zero readmissions or strong performance. Missing ratios leave the metric denominator; missing volume is retained unless a volume filter requires it.
4. **Why not average all six ratios together?** Conditions have different populations and reporting coverage. A composite would need a justified weighting method and a decision it is designed to support.
5. **What does ERR = 1.05 mean?** The CMS-published predicted rate is 1.05 times the expected rate. It is a relative comparison of modeled rates, not a five percentage-point patient rate or evidence of a payment penalty.
6. **Why SQL window functions?** Sort eligible hospital ratios, locate the central position(s), and calculate an odd- or even-cohort median without losing the row-level model.
7. **What changes when the volume minimum increases?** Hospitals with missing or low published volume leave the cohort. Both the denominator and the share above 1 can change. This is sensitivity to cohort selection, not proof of improved outcomes.
8. **What would you do next with access to a quality team?** Confirm service availability, read the relevant CMS footnotes, review newer results and use appropriately governed internal data to examine discharge and follow-up processes.

## Hands-on exercises

- Open COPD with no volume filter. Explain 34 / 68 = 50.0% and why the denominator is not 82.
- Switch to coronary bypass and a minimum of 250. Identify how many exclusions arise from missing ratios, missing volumes and low volumes.
- Open excluded records and inspect an original footnote in the CSV against the CMS data dictionary.
- Run the tests, then trace the no-volume-filter rule in both `analysis.py` and `sql/cohort_summary.sql`.
- Explain why the national context includes Indiana and why a small difference is not automatically statistically significant.
