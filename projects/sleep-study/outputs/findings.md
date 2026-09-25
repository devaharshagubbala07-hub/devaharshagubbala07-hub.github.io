# What changes when the context changes?

This is an educational reanalysis of a **synthetic** dataset, not a population study.

- **374 records, 132 distinct feature profiles.** The 242 repeated profiles beyond
  the first occurrence have different Person IDs. They are kept in the main model;
  removing them is a sensitivity analysis, not a confirmed data-cleaning correction.
- **Pooled Pearson r = 0.193.** The activity/sleep
  association is weak when all records are pooled. Female records show r =
  -0.235; male records show r =
  0.761. These are unadjusted descriptions.
- **Adjusted activity coefficient = 0.008529.** Holding age and stress
  fixed in the fitted model, 10 additional activity units correspond to
  0.085 more sleep-quality points. This is an association in the
  data, not an intervention benefit. Quality is an ordinal 1–10 score.
- **Adjusted stress coefficient = -0.578635.** Including stress as a
  predictor does not demonstrate mediation. There is no temporal/causal design.
- **Repeated-profile sensitivity:** the adjusted activity coefficient is
  0.010746 with one row per feature profile (n=132). Different weighting
  changes the coefficient; the sensitivity is descriptive, not a preferred estimate.
- **BMI labels remain separate:** Normal (195), Normal Weight (21), Overweight
  (148), Obese (10). There is no documented rule proving the first two labels are
  interchangeable. The smallest group is too thin to support broad comparisons.

## Reconciliation to the submitted presentation

All 12 checks reproduce the slide 9–11 ANOVA statistics,
regression coefficients and R-squared values within the displayed rounding.
The 370 residual degrees of freedom plus four fitted coefficients also agree with
374 model records. The introductory claim of 400 records is not repeated.

## Analyst decision

Do not translate these model outputs into workplace wellness recommendations.
For a real analysis, first verify data provenance, label definitions, sample sizes,
dependence between records and the decision being supported; then use a suitable
design and validation plan. A strong in-sample fit alone is not predictive validation.
