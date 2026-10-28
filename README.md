# Devaharsha Gubbala — Healthcare Analytics Portfolio

[Open the portfolio](https://devaharshagubbala07-hub.github.io/).

Reporting Analyst at Merative, **January 2026–Present**. The professional case notes describe claims reporting, cohort definitions, cost and utilization reporting, and dashboard migration checks. Client names, data and internal deliverables remain private.

## Featured projects

| Project | Data | Focus |
| --- | --- | --- |
| [Claims cost explorer](https://devaharshagubbala07-hub.github.io/demo/) | Synthetic enrollment and claims | PMPM denominators, quarantine rules and cost comparisons |
| [Prescription spending](https://devaharshagubbala07-hub.github.io/projects/prescription-spending/) | Public CMS aggregate data, 2020–2024 observations | Spending concentration, fill counts and average spending per fill |
| [Hospital readmissions](projects/readmissions/) | Public CMS hospital aggregates, July 2021–June 2024 observations | Condition-specific benchmarking and missing-data exclusions |

These independent portfolio projects were developed with AI assistance in September 2026. They are separate from employer work and graduate coursework. Their source manifests, methods, code and limitations are available in the linked repositories.

## Supporting and archived work

- [FHIR ETL & data quality](projects/fhir-quality/): original graduate team context plus a separate AI-assisted demo. Individual academic task ownership is not documented; the original team is credited.
- [AI workflow cost model](projects/ai-value/): a supporting synthetic scenario analysis with illustrative costs and workload assumptions.
- [Appointment operations](projects/operations/) and [reporting migration](projects/migration/) are additional synthetic exercises retained at their existing URLs.
- [Sleep & physical activity](projects/sleep-study/) is an archived academic case study and is not featured on the homepage.

The prescription-spending repository also contains an **unfinished Power BI extension**. File/schema checks do not verify Power BI Desktop refresh, DAX evaluation or rendering. It is not showcased as a completed report.

## Run locally

```bash
python -m http.server 8000
```

Open `http://localhost:8000/`. HTTP is required for dashboards that load JSON. Main content and baseline case-study charts remain readable without JavaScript. Motion respects reduced-motion preferences and the site's motion switch.

## Rebuild case studies

```bash
python projects/fhir-quality/pipeline.py
python projects/readmissions/download_source.py
python projects/readmissions/analysis.py
python projects/readmissions/build_page.py
python projects/build_case_studies.py
```

The last command builds FHIR and the archived Sleep page from their committed outputs. Original academic source code and annotated presentations are not distributed here. See each project's README for source requirements and tests.

## Check the site

```bash
python scripts/check_site.py
```

Requires Python 3.11+ and Node.js. Checks local links, anchors, assets, JSON and JavaScript syntax. Browser interactions and external destinations require separate checks.

## Maintenance

GitHub Pages publishes the root of `main`. Keep `.nojekyll`. The claims `demo/` mirrors the dashboard in `healthcare-claims-analytics`; prescription and AI project pages mirror their analysis repositories. Keep copies aligned when changing them.

The navy layout includes a generated, decorative analyst-workspace image. Its charts do not represent the project data. [Artwork details](assets/README.md).
