"""Reproduce and extend the graduate sleep study using the pinned public CSV.

The publisher describes these records as synthetic. All models are descriptive
teaching examples, not estimates of health effects in a real population.
Run: python analysis.py. Requires NumPy and SciPy; never downloads on execution.
"""
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent
SHA256 = "1efe7b6f781ff88078d08d81fe136cff98b1b0c32560f35f8650ca5984b77841"
NUMERIC = ["Age", "Sleep Duration", "Quality of Sleep", "Physical Activity Level",
           "Stress Level", "Heart Rate", "Daily Steps"]


def read_source(path=ROOT / "data/sleep-health-v2.csv"):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise ValueError("Source checksum differs from the reviewed version 2 file")
    with path.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    ids = [r["Person ID"] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Person ID must be unique")
    for row in rows:
        for key in NUMERIC:
            row[key] = float(row[key])
            if not np.isfinite(row[key]):
                raise ValueError(f"Nonfinite {key}")
        if not 1 <= row["Quality of Sleep"] <= 10:
            raise ValueError("Sleep quality outside the documented 1–10 scale")
    return rows


def ols(x, y, names):
    """Full-rank least squares, with classical SE to match the original R output."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    beta, _, rank, _ = np.linalg.lstsq(x, y, rcond=None)
    n, k = x.shape
    if rank != k or n <= k:
        raise ValueError("Model must have full column rank and residual degrees of freedom")
    residual = y - x @ beta
    sse = float(residual @ residual)
    sst = float((y - y.mean()) @ (y - y.mean()))
    covariance = (sse / (n - k)) * np.linalg.inv(x.T @ x)
    se = np.sqrt(np.diag(covariance))
    return {
        "n": n, "residual_df": n - k, "r_squared": 1 - sse / sst,
        "residual_standard_error": float(np.sqrt(sse / (n - k))),
        "coefficients": [
            {"term": name, "estimate": float(b), "standard_error": float(s)}
            for name, b, s in zip(names, beta, se)
        ],
    }


def model(rows, kind):
    y = [r["Quality of Sleep"] for r in rows]
    if kind == "adjusted":
        x = [[1, r["Physical Activity Level"], r["Age"], r["Stress Level"]] for r in rows]
        names = ["Intercept", "Physical activity", "Age", "Stress"]
    elif kind == "gender_interaction":
        x = [[1, r["Physical Activity Level"], int(r["Gender"] == "Male"),
              r["Physical Activity Level"] * int(r["Gender"] == "Male")] for r in rows]
        names = ["Intercept (Female)", "Activity (Female)", "Male intercept difference",
                 "Male activity slope difference"]
    else:
        x = [[1, r["Physical Activity Level"]] for r in rows]
        names = ["Intercept", "Physical activity"]
    return ols(x, y, names)


def group_summary(label, rows):
    activity = np.array([r["Physical Activity Level"] for r in rows])
    sleep = np.array([r["Quality of Sleep"] for r in rows])
    counts = Counter(zip(activity, sleep))
    fitted = model(rows, "simple")
    return {
        "label": label, "n": len(rows), "mean_sleep": float(sleep.mean()),
        "mean_activity": float(activity.mean()),
        "pearson_r": float(stats.pearsonr(activity, sleep).statistic),
        "spearman_rho": float(stats.spearmanr(activity, sleep).statistic),
        "slope": fitted["coefficients"][1]["estimate"],
        "intercept": fitted["coefficients"][0]["estimate"],
        "activity_min": float(activity.min()), "activity_max": float(activity.max()),
        "points": [{"activity": float(a), "sleep": float(s), "count": c}
                   for (a, s), c in sorted(counts.items())],
    }


def analyze(rows):
    groups = {"all": group_summary("All records", rows)}
    for column, prefix in [("Gender", "gender"), ("BMI Category", "bmi")]:
        for value in sorted({r[column] for r in rows}):
            key = prefix + "-" + value.lower().replace(" ", "-")
            groups[key] = group_summary(value, [r for r in rows if r[column] == value])
    # These are duplicate feature profiles, not proven duplicate people. Retain
    # all unique IDs in the main analysis; deduplicate only as a sensitivity.
    unique_profiles = {}
    for row in rows:
        key = tuple((k, v) for k, v in sorted(row.items()) if k != "Person ID")
        unique_profiles.setdefault(key, row)
    unique_rows = list(unique_profiles.values())
    adjusted = model(rows, "adjusted")
    interaction = model(rows, "gender_interaction")
    checks = []
    def check(name, actual, displayed, tolerance):
        checks.append({"check": name, "recomputed": actual, "slide_value": displayed,
                       "tolerance": tolerance, "passed": bool(abs(actual-displayed) <= tolerance)})
    for c, displayed in zip(adjusted["coefficients"], [9.430111, .008529, .011711, -.578635]):
        check("Slide 10: " + c["term"], c["estimate"], displayed, .00000051)
    check("Slide 10: R-squared", adjusted["r_squared"], .8398, .000051)
    for c, displayed in zip(interaction["coefficients"], [8.511286, -.014312, -3.718797, .051064]):
        check("Slide 11: " + c["term"], c["estimate"], displayed, .00000051)
    check("Slide 11: R-squared", interaction["r_squared"], .3197, .000051)
    occupations = sorted({r["Occupation"] for r in rows})
    anova = {}
    for metric, displayed, tol in [("Quality of Sleep", 30.02, .0051),
                                    ("Physical Activity Level", 18.8, .051)]:
        samples = [[r[metric] for r in rows if r["Occupation"] == o] for o in occupations]
        result = stats.f_oneway(*samples)
        anova[metric] = {"f": float(result.statistic), "df_between": len(samples)-1,
                         "df_within": len(rows)-len(samples)}
        check("Slide 9: occupation ANOVA for " + metric, float(result.statistic), displayed, tol)
    assert all(c["passed"] for c in checks), "Replication failed"
    return {
        "provenance": "Public synthetic educational dataset; independent Python reanalysis in 2026",
        "source_sha256": SHA256, "records": len(rows), "unique_profiles": len(unique_rows),
        "repeated_profiles_beyond_first": len(rows)-len(unique_rows),
        "bmi_counts": dict(Counter(r["BMI Category"] for r in rows)),
        "groups": groups, "adjusted_model": adjusted, "gender_interaction": interaction,
        "unique_profile_sensitivity": model(unique_rows, "adjusted"),
        "occupation_anova": anova, "reconciliation": checks,
    }


def main():
    result = analyze(read_source())
    output = ROOT / "outputs"
    output.mkdir(exist_ok=True)
    (output / "summary.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    a = result["adjusted_model"]["coefficients"]
    s = result["unique_profile_sensitivity"]["coefficients"]
    (output / "findings.md").write_text(f"""# What changes when the context changes?

This is an educational reanalysis of a **synthetic** dataset, not a population study.

- **374 records, 132 distinct feature profiles.** The 242 repeated profiles beyond
  the first occurrence have different Person IDs. They are kept in the main model;
  removing them is a sensitivity analysis, not a confirmed data-cleaning correction.
- **Pooled Pearson r = {result['groups']['all']['pearson_r']:.3f}.** The activity/sleep
  association is weak when all records are pooled. Female records show r =
  {result['groups']['gender-female']['pearson_r']:.3f}; male records show r =
  {result['groups']['gender-male']['pearson_r']:.3f}. These are unadjusted descriptions.
- **Adjusted activity coefficient = {a[1]['estimate']:.6f}.** Holding age and stress
  fixed in the fitted model, 10 additional activity units correspond to
  {10*a[1]['estimate']:.3f} more sleep-quality points. This is an association in the
  data, not an intervention benefit. Quality is an ordinal 1–10 score.
- **Adjusted stress coefficient = {a[3]['estimate']:.6f}.** Including stress as a
  predictor does not demonstrate mediation. There is no temporal/causal design.
- **Repeated-profile sensitivity:** the adjusted activity coefficient is
  {s[1]['estimate']:.6f} with one row per feature profile (n=132). Different weighting
  changes the coefficient; the sensitivity is descriptive, not a preferred estimate.
- **BMI labels remain separate:** Normal (195), Normal Weight (21), Overweight
  (148), Obese (10). There is no documented rule proving the first two labels are
  interchangeable. The smallest group is too thin to support broad comparisons.

## Reconciliation to the submitted presentation

All {len(result['reconciliation'])} checks reproduce the slide 9–11 ANOVA statistics,
regression coefficients and R-squared values within the displayed rounding.
The 370 residual degrees of freedom plus four fitted coefficients also agree with
374 model records. The introductory claim of 400 records is not repeated.

## Analyst decision

Do not translate these model outputs into workplace wellness recommendations.
For a real analysis, first verify data provenance, label definitions, sample sizes,
dependence between records and the decision being supported; then use a suitable
design and validation plan. A strong in-sample fit alone is not predictive validation.
""", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ["records", "unique_profiles", "bmi_counts"]}))
    print(f"{len(result['reconciliation'])} slide-output reconciliations passed")


if __name__ == "__main__":
    main()
