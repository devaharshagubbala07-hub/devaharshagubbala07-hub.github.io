# Sleep, activity & analytical judgment

[Open the case study](https://devaharshagubbala07-hub.github.io/projects/sleep-study/) · [Findings](outputs/findings.md) · [Source manifest](source.json)

**Question:** Does the relationship between physical activity and sleep quality look the same across groups?

The pooled correlation is weak (r = 0.193), and the direction differs between the recorded gender groups. Four BMI labels, a small subgroup and repeated feature profiles all change how the results should be interpreted. This project demonstrates reproducibility, segmentation and careful communication of model limitations.

## Original academic work and this extension

The original graduate team presentation was *Analysis of the Relationship Between Physical Activity and Sleep Quality Across Different BMI Categories*. Team members: Aishwarya Voraganti, Ritheesh Miridoodi, Devaharsha Gubbala, Asra Tasneem Shaik and Saranya Guvvala. The slides show R/RStudio analysis, correlation, ANOVA, regression, interaction and BMI comparisons. They do not identify each person's tasks; no sole-authorship claim is made here.

This **September 2026 Python reanalysis** was developed with AI assistance from the public source and the submitted presentation. It is newly written code, not the team's original R script. The raw source was independently downloaded from Kaggle version 2, pinned by checksum and rerun. Twelve numerical checks reproduce the rounded outputs on slides 9–11. The original annotated group PDF is not redistributed.

## Results and interpretation

| Evidence | Result | Interpretation |
| --- | --- | --- |
| Records / unique IDs | 374 / 374 | Corrects the introductory slide's count of 400 |
| Distinct feature profiles (excluding ID) | 132 | 242 repeated profiles beyond the first; retain for primary replication |
| Activity–sleep Pearson correlation | 0.193 overall; −0.235 Female; 0.761 Male | An aggregate result hides different subgroup patterns |
| Activity coefficient adjusted for age and stress | 0.008529 | About 0.085 sleep-score points per 10 activity units; descriptive association |
| Adjusted in-sample R-squared | 0.8398 | Model fit, not held-out accuracy or evidence of a real health effect |
| Smallest BMI group | Obese: 10 records | Avoid broad conclusions from a thin synthetic subgroup |

The publisher explicitly describes the data as **synthetic, created for illustration**. This is not a measured clinical cohort. Real-world inference, intervention recommendations and a claim that stress mediates an effect are unsupported. Repeated profiles also make a claim of independent real participants inappropriate.

## Run

Python 3.11+; reference environment: Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0.

```bash
cd projects/sleep-study
python -m pip install -r requirements.txt
python analysis.py
python -m unittest -v
```

The CSV is small and included, so analysis runs without network access. A checksum mismatch stops execution. `outputs/summary.json` drives the website; `outputs/findings.md` summarizes results. Seven tests cover a hand-calculated line, an independent SciPy comparison, source integrity, denominators, label preservation, interaction parameterization and rank-deficient designs.

## Method choices

- Preserve the source CSV bytes and literal `None` sleep-disorder category; it is not a missing value.
- Retain all 374 unique IDs for replication. Count repeated profiles separately; do not silently delete them.
- Keep `Normal` and `Normal Weight` separate because their equivalence is not documented.
- Fit least squares using NumPy; report classical standard errors only to reconcile with the original R output. No confidence intervals or significance claims are presented as real-population evidence.
- Fit activity × recorded gender separately from the activity + age + stress model. The interactive subgroup lines are **unadjusted**, not slices of the adjusted model.
- Use one record per distinct profile only for an explicitly labeled weighting sensitivity.
- Treat the bounded ordinal sleep score as numeric to reproduce the original analysis; a real study would need to justify that choice and assess an ordinal model, dependence, confounding and validation.

## What I would do next with real data

Confirm provenance and data definitions, resolve BMI labels with the data owner, review group sizes and repeated measurements, and define the actual decision before selecting an inferential or predictive design. The current data cannot establish whether changing activity improves sleep.

## Sources

- [Kaggle source, version 2](https://www.kaggle.com/datasets/uom190346a/sleep-health-and-lifestyle-dataset) — CC0 listing; synthetic-data disclaimer.
- Uploaded original team slide deck: slide 9 (ANOVA), 10 (adjusted regression), 11 (gender interaction), 13 (BMI comparison). [Provenance](provenance.json).
- [NumPy least-squares documentation](https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html).
- [SciPy Pearson correlation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html) and [Spearman correlation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html).

### Data attribution

The bundled CSV is unchanged data by Kaggle publisher `uom190346a`, offered under the publisher's CC0: Public Domain listing. Its inclusion does not imply that the publisher endorses this analysis. Original academic team work is credited above; the reanalysis and presentation are separate.
